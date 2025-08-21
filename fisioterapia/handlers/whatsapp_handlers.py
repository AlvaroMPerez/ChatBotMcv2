# handlers/message_handler.py
from services.whatsapp_service import (
    send_whatsapp_message,
    send_whatsapp_buttons)
from models.user_state import (
    get_user_state,
    set_user_state,
    clear_user_state    
)
from utils.helpers import is_8_hours
import emoji, os
import datetime
import re

BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class MessageHandler:
    # ---------- Inicialización ----------
    def __init__(self, wa_id: str, name: str, message: dict, body: str | None, horario: bool, ts_raw: int, hora_local) -> None:
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
            self._handle_fis_states()

        # 3. Procesar botones
        if message["type"] == "interactive":
            self._handle_buttons()

    # ---------- Parte 1 – Saludos, información, promociones, ubicación, dudas, especialdiades ----------
    def _handle_text_greetings(self) -> None: 
        """ 
        Maneja los mensajes de texto que contienen promociones
        """  
        
        passed, msg = is_8_hours(self.wa_id)
        
        if passed: 
            print(f"✅ Usuario desbloqueado: {msg}")
            user_state = get_user_state(self.wa_id)
            print (f"📝 Estado del usuario: {user_state!r}")    
            if self.wants_promotions():
                
                # Continua con el flujo normal
            
                if self.horario == True:  # Esto lo tengo que cambiar por debugging <-------
                    from flows.fisioterapia import Fisioterapia
                    fis: Fisioterapia = Fisioterapia(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes información sobre nuestras promociones vigentes de fisioterapia."
                    )
                    # Aquí hace falta la parde de promociones 
                    
                    # ---- Inicia flujo del bot ------
                    
                    fis.politica_privacidad()
                    fis.tiene_cita()          
                    
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(. "
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
                
            elif self.wants_location():
                """
                Maneja los mensajes que contienen ubicación
                """
                if self.horario:
                    from flows.fisioterapia import Fisioterapia
                    fis: Fisioterapia = Fisioterapia(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes nuestra ubicación. "
                        "https://maps.app.goo.gl/a3239cawd54ucPxH9"
                    )
                    fis.politica_privacidad()
                    fis.mas_informacion()
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
                    from flows.fisioterapia import Fisioterapia
                    fis: Fisioterapia = Fisioterapia(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,("Bienvenido a Medical Care. Gustosamente le apoyo"
                                                                                "para que pueda agendar su cita."))
                    fis.politica_privacidad()
                    fis.tiene_cita()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.greetings():
                from flows.fisioterapia import Fisioterapia
                fis: Fisioterapia = Fisioterapia(self)
                is_8_hours(self.wa_id)
                if self.horario:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! ¿En qué puedo ayudarte hoy?"
                    )
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.wants_specialties():
                is_8_hours(self.wa_id)
                from flows.fisioterapia import Fisioterapia
                fis: Fisioterapia = Fisioterapia(self)
                if self.horario:
                    fis.politica_privacidad()
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes información sobre nuestras especialidades."
                    )
                    fis.tiene_cita()
                    
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.wants_help():
                from flows.fisioterapia import Fisioterapia
                fis: Fisioterapia = Fisioterapia(self)
                is_8_hours(self.wa_id)
                if self.horario:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}!"
                    )
                    fis.politica_privacidad()
                    fis.agente_atiende()
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
                 
        

    # ---------- Parte 2 – Estados de Fisioterapia ----------
    def _handle_fis_states(self) -> None:
        """
        Gestiona los estados del usuario, dependiendo del estado cambia el flujo del bot.
        """
        from flows.fisioterapia import Fisioterapia

        fis: Fisioterapia = Fisioterapia(self)
        state = get_user_state(self.wa_id)
        print(f"📝 Estado del usuario: {state!r}")
        print(f"📝 Ejecutando estado {get_user_state(self.wa_id)!r}")
        match state:       
            case "esperando_nombre":
                clear_user_state(self.wa_id)
                self.name = self.clean_name(self.body)
                if not self.name:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        "Por favor, envíe su nombre para continuar.")
                    set_user_state(self.wa_id, "esperando_nombre")
                    return   
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                    f"Gracias {self.name or 'paciente'} por tu nombre. "
                )
                fis.pedir_fecha_nacimiento()
            
            case "esperando_fecha_nacimiento":
                clear_user_state(self.wa_id)
                fis.pedir_correo()
            case "esperando_correo":
                clear_user_state(self.wa_id)
                fis.agente_atiende()
        
        
    # ---------- Parte 3 – Botones ----------
    def _handle_buttons(self) -> None:
        message_id = self.button_id

        # Laboratorio → todos los botones empiezan con "2"
        if message_id and message_id.startswith("2"):
            from flows.fisioterapia import Fisioterapia
            Fisioterapia(self).fis_flow()
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
    
    # ---------- Especialidades ----------
    def wants_specialties(self) -> bool:
        SPECIALTIES_KEYWORDS = ["especialidades", "especialidad", "servicios", "servicio"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in SPECIALTIES_KEYWORDS for tok in tokens)
    
    # ---------- Ayuda ----------
    def wants_help(self) -> bool:
        HELP_KEYWORDS = ["ayuda", "soporte", "asistencia", "necesito ayuda", "necesito soporte","duda", "pregunta","help"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in HELP_KEYWORDS for tok in tokens)
    
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