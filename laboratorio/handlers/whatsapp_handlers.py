# handlers/message_handler.py
from services.whatsapp_service import (
    send_whatsapp_message,
    send_whatsapp_buttons,
    send_whatsapp_img)
from models.user_state import (
    get_user_state,
    set_user_state,
    clear_user_state
)
from microsoft.enviar_promociones import link_promociones
from utils.helpers import is_8_hours
from flows.dudas import espere_un_momento
from typing import Optional, cast, List
from dotenv import load_dotenv
import emoji, os
import datetime
import re
import pdb
import asyncio
import time

load_dotenv()
BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class MessageHandler:
    # ---------- Inicialización ----------
    def __init__(self, wa_id: Optional[str], name, message: dict, body: str | None, horario: bool, ts_raw: int, hora_local) -> None:
        self.wa_id   = wa_id
        self.message = message
        self.body    = body or ""
        self.name    = self.clean_name(name)
        self.horario = horario
        self.ts_raw = ts_raw
        self.hora_local = hora_local
        

        # 1. Procesar saludos / info
        if message["type"] == "text":
            self._handle_text_greetings()

        # 2. Procesar estados 
        if message["type"] in ("text", "image"):
            self._handle_lab_states()

        # 3. Procesar botones
        if message["type"] == "interactive":
            self._handle_buttons()

    # ---------- Parte 1 – Saludos, información, promociones, ubicación----------
    def _handle_text_greetings(self) -> None: 
        """ 
        Maneja los mensajes de texto que contienen promociones
        """  
        if BUSINESS_PHONE_NUMBER_ID is None:
            raise ValueError("BUSINESS_PHONE_NUMBER_ID no puede ser None. Asegúrate de definirlo correctamente.")
        if self.wa_id is None:
            raise ValueError("wa_id cannot be None")
        passed, msg = is_8_hours(self.wa_id)
        if passed: 
            if get_user_state(self.wa_id) is None:
                set_user_state(self.wa_id, "inicio")
            # clear_user_state(self.wa_id)  # Limpiamos el estado del usuario si ya pasaron 8 horas
            print(f"✅ Usuario desbloqueado: {msg}")
            
            user_state = get_user_state(self.wa_id)
            if user_state is None:
                raise ValueError("user_state no puede ser None")
            user_state = cast(str, user_state)

            print(f"📝 Estado del usuario: {user_state!r}")    
            
            if self.wants_promotions():
                # Continua con el flujo normal
                if self.horario == True:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    links: List[str] = asyncio.run(link_promociones()) or []
                    # Iniicia el flujo 
                    if len(links) > 1:
                        time.sleep(0.5)
                        # Si hay más de una promoción manda imágenes
                        mensaje = "Con gusto te comparto las promociones vigentes de este mes para que las conozcas ✨."
                        print(f"Enviando mensaje: phone_id={BUSINESS_PHONE_NUMBER_ID}, wa_id={self.wa_id}, texto='{mensaje}'")
                        response = send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, mensaje)
                        for link in links:
                            send_whatsapp_img(BUSINESS_PHONE_NUMBER_ID,self.wa_id,link)
                            pass
                            # Si no, sólo envia que no hay promociones
                    else:
                        mensaje = f"¡Hola {self.name or 'paciente'}! por el momento no tenemos promociones vigentes, pero nuestros precios son los mejores!"
                        print(f"Enviando mensaje: phone_id={BUSINESS_PHONE_NUMBER_ID}, wa_id={self.wa_id}, texto='{mensaje}'")
                        response = send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, mensaje)
                    time.sleep(0.5)
                    lab.politica_privacidad()
                    lab.apoyar_con_algo_mas()
                    # ¿Te puedo apoyar con algo más?
                
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(. "
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
                
            elif self.wants_location():
                if get_user_state(self.wa_id) is None:
                    set_user_state(self.wa_id, "inicio")
                """
                Maneja los mensajes que contienen ubicación
                """
                if self.horario:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes nuestra ubicación. "
                        "https://maps.app.goo.gl/a3239cawd54ucPxH9"
                    )
                    self.mandar_promociones()
                    lab.politica_privacidad()
                    # ---- Inicia flujo del bot ------
                    lab.apoyar_con_algo_mas()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        (f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(. "
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                        "pero aquí tienes neustra ubicación. https://maps.app.goo.gl/a3239cawd54ucPxH9")  
                    )
            
            elif self.wants_appointment():
                """
                Maneja mensajes de texto que contengan palabras clave relacionadas con citas
                """
                is_8_hours(self.wa_id)
                if self.horario:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    self.mandar_promociones()
                    lab.politica_privacidad()
                    lab.ha_sido_paciente_wants_appointment()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.wants_budget():
                """
                Maneja los flujos para presupuestos.
                """
                is_8_hours(self.wa_id)
                if self.horario:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    
                    self.mandar_promociones()
                    lab.politica_privacidad()
                    lab.cuenta_con_orden_medica()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.greetings():
                is_8_hours(self.wa_id)
                if self.horario:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"Hola {self.name or 'paciente'} gracias por comunicarte a Medical Care Laboratory. ¿en qué puedo ayudarte hoy?"
                    )
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            return  
        else:
            # Usuario bloqueado, no puede enviar mensajes
            print(f"❌ Usuario bloqueado: {msg}")
            send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, msg)
            return

    # ---------- Parte 2 – Estados de Laboratorio ----------
    def _handle_lab_states(self) -> None:
        """
        Gestiona los estados del usuario, dependiendo del estado cambia el flujo del bot.
        """
        from flows.laboratorio import Laboratorio
        if self.wa_id is None:
            raise ValueError("wa_id cannot be None")
        lab  = Laboratorio(self)
        state = cast(str, get_user_state(self.wa_id))
        if state is None:
            return
        
        match state:
            case"esperando_orden_medica":
                clear_user_state(self.wa_id)
                # lab.estudio_interes()
                lab.pedir_nombre()
                
            case "esperando_estudio_interes":
                clear_user_state(self.wa_id)
                lab.pedir_nombre()
                
            case "esperando_nombre":
                clear_user_state(self.wa_id)
                self.name = self.clean_name(self.body)
                # Exportamos la variable global para poder usar el nombre en otras clases
                if not self.name:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        "Por favor, envíe su nombre para continuar.")
                    set_user_state(self.wa_id, "esperando_nombre")
                    return   
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                    f"Gracias {self.name or 'paciente'} por tu nombre. "
                )
                lab.pedir_fecha_nacimiento()
            
            case "esperando_fecha_nacimiento":
                clear_user_state(self.wa_id)
                lab.agente_atiende()
        
        
    # ---------- Parte 3 – Botones ----------
    def _handle_buttons(self) -> None:
        message_id = self.button_id

        # Laboratorio → todos los botones empiezan con "2"
        if message_id and message_id.startswith("2"):
            from flows.laboratorio import Laboratorio
            Laboratorio(self).lab_flow()
            return

    # ---------- Utilidades ----------
    @property
    def button_id(self) -> str | None:
        if self.message.get("type") == "interactive":
            return self.message.get("interactive", {}) \
                               .get("button_reply", {}) \
                               .get("id")
        return None

    #----- Promociones vigentes -----
    def wants_promotions(self) -> bool:
        PROMOTION_KEYWORDS = ["promociones", "promos", "info", "promoción", "promocion","información", "informacion",
                              "promo", "oferta", "ofertas", "descuento", "descuentos"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in PROMOTION_KEYWORDS for tok in tokens)
    
    def wants_budget(self) -> bool:
        PROMOTION_KEYWORDS = ["cotización","cotizacion","cotisasion","cotisiasion"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in PROMOTION_KEYWORDS for tok in tokens)
    
    # ------- Ubicación -------
    def wants_location(self) -> bool:
        LOCATION_KEYWORDS = ["ubicación", "dirección", "direcciónes","locacion","ubicacion","diraccion","direccion",
                             "unbicación"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in LOCATION_KEYWORDS for tok in tokens)

    # ---------- cita ----------
    def wants_appointment(self) -> bool:
        APPOINTMENT_KEYWORDS = ["cita", "turno", "agendar", "reservar", "horario"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in APPOINTMENT_KEYWORDS for tok in tokens)
    
    # --------- Saludos ---------
    def greetings(self) -> bool:
        GREETING_KEYWORDS = ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in GREETING_KEYWORDS for tok in tokens)
    # ---------- Helpers ----------
    @staticmethod
    def is_emoji(ch: str) -> bool:
        return ch in emoji.EMOJI_DATA

    def clean_name(self, name: str) -> str:
        if not name:
            return ""
        if self.is_emoji(name):
            return ""
        return name.split()[0]
    
    def mandar_promociones(self) ->None:
        """
        Hace un listado de links dentro de la carpeta promociones, luego la recore y finalmente
        """
        from flows.laboratorio import Laboratorio
        lab: Laboratorio = Laboratorio(self)
        links: List[str] = asyncio.run(link_promociones()) or []
        # Guarda los links para mandarlos en una lista
        if len(links) > 1:
            time.sleep(0.5)
            # Si hay más de una promoción manda imágenes
            mensaje = "Con gusto atiendo tu solicitud, también te comparto las promociones vigentes de este mes para que las conozcas ✨"
            print(f"Enviando mensaje: phone_id={BUSINESS_PHONE_NUMBER_ID}, wa_id={self.wa_id}, texto='{mensaje}'")
            response = send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, mensaje)
            for link in links:
                send_whatsapp_img(BUSINESS_PHONE_NUMBER_ID,self.wa_id,link)
                pass
        
        # Si no, sólo envia que no hay promociones
        else:
            mensaje = f"¡Hola {self.name or 'paciente'}! por el momento no tenemos promociones vigentes, pero nuestros precios son los mejores!"
            print(f"Enviando mensaje: phone_id={BUSINESS_PHONE_NUMBER_ID}, wa_id={self.wa_id}, texto='{mensaje}'")
            response = send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, mensaje)
        time.sleep(0.5)