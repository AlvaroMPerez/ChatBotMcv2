# flows/laboratorio.py
from services.whatsapp_service import send_whatsapp_message, send_whatsapp_buttons
from handlers.whatsapp_handlers import MessageHandler
from models.user_state import (
    set_user_state, 
    get_user_state, 
    clear_user_state)
from models.bloqueos import (clear_bloqueo,
                             set_bloqueo)
import os
import pdb

BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class Fisioterapia:
    def __init__(self, handler: MessageHandler):
        self.handler    = handler
        self.wa_id      = handler.wa_id
        self.button_id  = (handler.button_id or "").strip()
        self.ts_raw     = handler.ts_raw

    # ---------- Router principal ----------
    def fis_flow(self) -> None:
        print(f"🧪 Ejecutando lab_flow con button_id: {self.button_id!r}")
        print(f"🧪 Estado del usuario: {get_user_state(self.wa_id)!r}")
        

        match self.button_id:
           # Aquí van los casos de los botones 
            
            case "2.5_tiene_duda_si":
                self.agente_atiende()
                
            case "2.6_tiene_duda_no":
                self.finalizar()
            
            case "2.1_paciente_si" | "2.2_paciente_no":
                self.valoracion_especialidades()
            
            case "2.1_info_si":
                self.ha_sido_paciente()
                
            case "2.2_info_no":
                self.tiene_duda()
            
            case "2.2_especialidades":
                self.info_espacialidades()
                self.desea_agendar()
                            
            case "2.1_cita_si":
                self.agente_atiende()
            
            case "2.2_cita_no":
                self.ha_sido_paciente()       
                        
            case "2.3_cambiar_cita":
                self.agente_atiende()
            
            case "2.1_valoracion":
                self.info_valoracion()
                
            case "2.1_agendar_si":
                self.pedir_nombre()
            
            case "2.2_agendar_no":
                self.tiene_duda()
            
            case _:
                print("‼️ Sin coincidencia en Fisioterapia")
                
    # ---------- Politica de privacidad ----------
    def politica_privacidad(self) -> None:
        body = ("Por favor, lea nuestra política de privacidad "
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tristique dapibus purus eget egestas. Lorem ipsum dolor sit amet, consectetur.")
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
     
    # ---------- Más información --------
    def mas_informacion(self) -> None:
        body = "¿Le gustaría más información?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_info_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_info_no", "title": "No"}},
            {"type": "reply", "reply": {"id": "2.3_cambiar_cita", "title": "Cambiar cita"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ---------- Desea valoración o especialidades ----------
    def valoracion_especialidades(self) -> None:
        body = "¿Desea una valoración o información sobre nuestras especialidades?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_valoracion", "title": "Valoración"}},
            {"type": "reply", "reply": {"id": "2.2_especialidades", "title": "Especialidades"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
        
    # --------- Información valoración ----------
    def info_valoracion(self) -> None:
        body : str = "El costo de la valocarion es de $PRECIO MXN. ¿Desea angendar?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_agendar_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_agendar_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # --------- Información especialidades ----------    
    def info_espacialidades(self) -> None:
        body = ("Nuestras especialidades incluyen: "
                "Fisioterapia, Rehabilitación, Terapia Ocupacional."
                "Tienen un costo de $PRECIO MXN cada una.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
    
    def desea_agendar(self) -> None:
        body = "¿Desea agendar una cita?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_agendar_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_agendar_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
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
        body = "Un agente de atención al cliente le atenderá en breve."
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)
        clear_bloqueo(self.wa_id)
        set_bloqueo(self.wa_id, self.ts_raw)
    
    
    # ----------- Pedir nombre -----------
    def pedir_nombre (self) -> None:
        body = ("Por favor, proporcione su nombre completo "
                "para que podamos identificarlo correctamente.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_nombre")
    
    # ----------- Pedir fecha nacimiento -----------
    def pedir_fecha_nacimiento(self) -> None:
        body = ("Por favor, proporcione su fecha de nacimiento "
                "para que podamos identificarlo correctamente.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_fecha_nacimiento")
        
    # ----------- Pedir correo -----------
    def pedir_correo(self) -> None:
        body = ("Por favor, proporcione su correo electrónico "
                "para que podamos enviarle la información de su cita.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_correo")
    
    # ------ Finalizar flujo -----
    def finalizar(self) -> None:
        body = "Gracias por contactarnos. ¡Que tenga un buen día!"
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)