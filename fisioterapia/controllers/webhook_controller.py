from flask import Flask, request, jsonify, abort, Blueprint
import pdb
import json
import hmac
import os
import hashlib
from dotenv import load_dotenv
from datetime import datetime
from models.message_model import save_message_id, message_id_exist
from services.whatsapp_service import send_whatsapp_message
from handlers.whatsapp_handlers import MessageHandler
from flows.fisioterapia import Fisioterapia
from models.user_state import (print_all_user_states,
                               clear_user_state)
from datetime import datetime
from utils.helpers import (esta_en_horario,
                           unix_to_america)

load_dotenv()

APP_SECRET = os.getenv('APP_SECRET')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
BUSINESS_PHONE_NUMBER_ID = os.getenv('BUSINESS_PHONE_NUMBER_ID')

# Webhook blueprint
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Maneja los mensajes entrantes de WhatsApp"""

    # Verifica los payloads SHA256
    signature = request.headers.get("X-Hub-Signature-256")
    if signature and "=" in signature:
        sha_name, sha_signature = signature.split('=')
    else:
        print("invalid header")
        return "forbbiden",403
    
    if not signature:
        print("firma recibida:", signature)
        abort(400,"Falta firma")
    
    if sha_name != "sha256":
        print("firma recibida:", signature)
        abort(400, "Algoritmo sha no soportado")

    # Genera la firma propia usando APP_SECRET & hmac https://docs.python.org/3/library/hmac.html
    if APP_SECRET is None:
        raise ValueError("APP_SECRET no puede ser None. Asegúrate de definirlo correctamente.")
    mac = hmac.new(APP_SECRET.encode(), request.data, hashlib.sha256)
    expected_hash = mac.hexdigest()
    if not hmac.compare_digest(expected_hash, sha_signature):
        abort(400, "Firma no valida")

    # freccuency
    payload = request.json
    if payload == None:
            print("No payload found")
            abort(400, "No payload found")
    print(json.dumps(payload, indent=2))

    if payload.get("object") != "whatsapp_business_account":
        
        return jsonify({"status":"ignored"}), 200
    
    # Tomando los datos del payload
    name:str= ""
    wa_id:str = ""
    body:str = ""
    horario = None

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value",{})
            messages = value.get("messages",[])
            for contact in value.get("contacts",[]):
                name = contact.get("profile",{}).get("name")
                wa_id = contact.get("wa_id")
                if wa_id.startswith("521"):
                    wa_id = "52" + wa_id[3:]
            for message in messages:
                message_id = message.get("id")
                ts_raw:int = int(message.get("timestamp"))
                horario = esta_en_horario(ts_raw)
                print(f"El {horario}")
                exist = message_id_exist(message_id)
                body = ""
                if message.get("type") == "text":
                    body = message.get("text",{}).get("body")
                if  exist:  
                    continue
                save_message_id(message_id)
                hora_local: datetime = unix_to_america(ts_raw)
                handler = MessageHandler(wa_id      = wa_id,
                                         name       = name,
                                         message    = message,
                                         body       = body,
                                         horario    = horario,
                                         ts_raw     = ts_raw,
                                         hora_local = hora_local)
                lab = Fisioterapia(handler)
                
    return jsonify({"status": "ok"}), 200

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_verification():
    """Verificación del webhook"""
    # Información sobre verifcación de payloads
    # https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # Verify if mode and token are right
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        # Responder con 200 OK y el challenge token de la petición
        return "OK", 200
    else:
        return "Forbidden", 403

@webhook_bp.route('/', methods=['GET'])
def home():
    """Página de inicio"""
    return """<pre>Nothing to see here.
Checkout README.md to start.</pre>"""

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint adicional para verificar que el servicio esté funcionando"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WhatsApp Webhook"
    }), 200