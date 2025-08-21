import os
import requests
import json
from dotenv import load_dotenv
import pdb

load_dotenv()

WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
GRAPH_API_TOKEN=os.getenv('GRAPH_API_TOKEN')
API_VERSION = os.getenv('API_VERSION')
BUSINESS_PHONE_NUMBER_ID = os.getenv('BUSINESS_PHONE_NUMBER_ID')

def send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, recipient, message_body, context_message_id=None):
    # Envía un mensaje de WhatsApp
    url = f"https://graph.facebook.com/{API_VERSION}/{BUSINESS_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "text": {"body": message_body}
    }
    
    # Agregar contexto si se proporciona (para responder a un mensaje específico)
    if context_message_id:
        data["context"] = {"message_id": context_message_id}
    #breakpoint()
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return None
    
    
def send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, recipient, body_text, buttons):
    url = f"https://graph.facebook.com/{API_VERSION}/{BUSINESS_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type":"button",
            "body":{
                "text": body_text
            },
            "action":{
                "buttons":buttons
            }
        },
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return None

def mark_message_as_read(BUSINESS_PHONE_NUMBER_ID, message_id):
    """Marca un mensaje como leído"""
    url = f"https://graph.facebook.com/{API_VERSION}/{BUSINESS_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error marcando mensaje como leído: {e}")
        return None