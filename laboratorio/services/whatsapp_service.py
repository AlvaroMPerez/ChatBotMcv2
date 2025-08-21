import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
GRAPH_API_TOKEN=os.getenv('GRAPH_API_TOKEN')
API_VERSION=os.getenv('API_VERSION')
BUSINESS_PHONE_NUMBER_ID = os.getenv('BUSINESS_PHONE_NUMBER_ID')

def send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, recipient, message_body):
    # Envía un mensaje de WhatsApp
    print(f"Enviando mensaje a {recipient}, Bussiness ID: {BUSINESS_PHONE_NUMBER_ID}, Mansaje: {message_body} ")
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

    try: 
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el mensaje: {e}")
        return {"error": "No se pudo enviar el mensaje"}
    
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

def send_whatsapp_img(BUSINESS_PHONE_NUMBER_ID, recipient,link):
    url = f"https://graph.facebook.com/{API_VERSION}/{BUSINESS_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": recipient,
    "type": "image",
    "image": {
        "link": link
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
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