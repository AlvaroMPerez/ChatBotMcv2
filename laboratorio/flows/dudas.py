from services.whatsapp_service import send_whatsapp_message

import os

BUSINESS_PHONE_NUMBER_ID = os.getenv('BUSINESS_PHONE_NUMBER_ID')

def espere_un_momento(wa_id):
    message_body = "Por favor, espere un momento."
    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID,wa_id,message_body,context_message_id=None)
    return