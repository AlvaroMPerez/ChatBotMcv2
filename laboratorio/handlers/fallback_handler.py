from services.whatsapp_service import send_whatsapp_message
import os 
from dotenv import load_dotenv

load_dotenv()
BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")

class Fallback_Handler:
    def __init__(self, wa_id, name, ts_raw):
        self.wa_id = wa_id
        self.name = name
        self.ts_raw = ts_raw

    def fallback(self) -> None:
        message = (
            "Disculpa, no entendí tu mensaje 😳.\n\n"
            "Puedes intentar escribiendo: \n"
            "- Promociones\n"
            "- Cita\n"
            "- Ubicación\n"
            "- Cotización\n"
            "- Hablar con un asesor"
        )

        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,message)