# flows/laboratorio.py
from services.whatsapp_service import (send_whatsapp_message, send_whatsapp_buttons,send_whatsapp_img)
from handlers.whatsapp_handlers import MessageHandler
from models.user_state import (
    set_user_state, 
    get_user_state, 
    clear_user_state)
from models.bloqueos import (clear_bloqueo,
                             set_bloqueo)
import os
import asyncio
from typing import  List
from dotenv import load_dotenv

load_dotenv()

BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class Laboratorio:
    def __init__(self, handler: MessageHandler):
        self.handler    = handler
        self.wa_id      = handler.wa_id
        self.button_id  = (handler.button_id or "").strip()
        self.ts_raw     = handler.ts_raw
        self.name       = handler.name

    # ---------- Router principal ----------
    def lab_flow(self) -> None:
        print(f"🧪 Ejecutando lab_flow con button_id: {self.button_id!r}")
        print(f"🧪 Estado del usuario: {get_user_state(self.wa_id)!r}")
        

        match self.button_id:
        # Aquí van los casos de los botones 
            case "2.1_info_si" | "2.1.1_paciente_si" | "2.2.2_paciente_no":
                self.cuenta_con_orden_medica()
                
            case "2.3_orden_medica_si":
                self.orden_medica_si()
            
            case "2.4_orden_medica_no":
                clear_user_state(self.wa_id)
                self.estudio_interes()
            
            case "2.2_info_no":
                self.tiene_duda()
                
            case "2.5_tiene_duda_si":
                self.agente_atiende()
                
            case "2.6_tiene_duda_no":
                self.finalizar()
            
            case "2.1_paciente_si" | "2.2_paciente_no":
                self.mas_informacion()
            
            case "2.1_cita_si" | "2.2_cita_no":
                self.politica_privacidad()
                self.agente_atiende()
            case "2.3_cambiar_cita":
                self.agente_atiende()
            case "2.1.1_appointment_paciente_si" | "2.2.2_appointment_paciente_no" | "2.2_agendar_cita":
                """Flujo exclusivo de los botones wants_appointment"""
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID,self.wa_id,"Siguiendo con tu cita, primero necesitamos cotizar"
                                                                            " tus laboratorios 🧪")
                self.cuenta_con_orden_medica()
            case "2.1_cotizar_labs" :
                self.cuenta_con_orden_medica()
            case "2.3_servicio_domicilio":
                self.agente_atiende_domicilio()
            case _:
                print("‼️ Sin coincidencia en Laboratorio")
                
    # ---------- Politica de privacidad ----------
    def politica_privacidad(self) -> None:
        body = ("Le informamos que sus datos serán tratados, para brindarle una mejor atención y seguimiento, conforme al "
        "Aviso de Privacidad de Medical Care, el cual estará disponible en breve en medicalcare.mx/privacidad.php")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
    
    # ---------- Tiene cita? ----------
    def tiene_cita(self) -> None:
        body = "¿Tiene una cita programada?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_cita_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_cita_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ---------- Ha sido paciente? ----------
    def ha_sido_paciente(self) -> None:
        body = "¿Ha sido paciente de Medical Care anteriormente?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_paciente_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_paciente_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)

        # --- Ha sido paciente Agendar cita EXCLUSIVO ----
    def ha_sido_paciente_cita(self) -> None:
        body = "¿Ha sido paciente de Medical Care anteriormente?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.2.1_paciente_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.3.2_paciente_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    def ha_sido_paciente_wants_appointment(self) -> None:
        """
        Este es un flujo exclusivo del las opciones "wants_appointment"
        """
        body = "¿Ha sido paciente de Medical Care anteriormente?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1.1_appointment_paciente_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2.2_appointment_paciente_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)

    # ---------- Más información --------
    def mas_informacion(self) -> None:
        body = "¿Le gustaría más información?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_info_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_info_no", "title": "No"}},
            {"type": "reply", "reply": {"id": "2.3_cambiar_cita", "title": "Cambiar cita"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ---------- Cuenta con orden Médica? ----------
    def cuenta_con_orden_medica(self) -> None:

        body = "¿Cuenta con una orden médica?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.3_orden_medica_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.4_orden_medica_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    def orden_medica_si(self) -> None:
        body = ("Para poder procesar tu solicitud, por favor envía una foto de tu orden médica o escríbenos "
                "aquí los estudios que deseas realizar.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_orden_medica")
    # --------- Tiene alguna duda? ---------
    def tiene_duda(self) -> None:
        body = "¿Tiene alguna duda?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.5_tiene_duda_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.6_tiene_duda_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ----------- Agente atiende ---------
    def agente_atiende(self) -> None:
        body = (f"Gracias, {self.name}. En breve, uno de nuestros agentes te apoyará con la cotización y dará seguimiento a tu solicitud ☺️")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)
        clear_bloqueo(self.wa_id)
        set_bloqueo(self.wa_id, self.ts_raw)
    
    # ----------- Estudio de interés -----------
    def estudio_interes(self) -> None:
        '''
        En deshuso por redundancia
        '''
        set_user_state(self.wa_id, "esperando_estudio_interes")
        body = ("Podría decirme los estudios que desea cotizar por favor🔬")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
    
    # ----------- Pedir nombre -----------
    def pedir_nombre (self) -> None:
        body = ("Gracias, continuando con tu solicitud, por favor podrías proporcionarme tu nombre completo")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_nombre")
    
    # ----------- Pedir fecha nacimiento -----------
    def pedir_fecha_nacimiento(self) -> None:
        body = ("Ahora, podrías compartirme tu fecha de nacimiento, por favor.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_fecha_nacimiento")

    def apoyar_con_algo_mas(self) -> None:
        body = ("¿Puedo apoyarte con algo más?")
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_cotizar_labs", "title": "Cotizar Labs"}},
            {"type": "reply", "reply": {"id": "2.2_agendar_cita", "title": "Agendar cita"}},
            {"type": "reply", "reply": {"id": "2.3_servicio_domicilio", "title": "Servicio a domicilio"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    def agente_atiende_domicilio(self)-> None:
        body = (f"Gracias, {self.name}. En breve, uno de nuestros agentes te apoyará y dará seguimiento a tu solicitud ☺️")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)
        clear_bloqueo(self.wa_id)
        set_bloqueo(self.wa_id, self.ts_raw)
        
    # ------ Finalizar flujo -----
    def finalizar(self) -> None:
        body = "Gracias por contactarnos. ¡Que tenga un buen día!"
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)