from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from models.user_state import clear_user_state
from models.bloqueos import (get_bloqueo)
from models.last_message import (set_user_last_message,
                                get_user_last_message)
from typing import Optional, List
from time import sleep
from services.whatsapp_service import (send_whatsapp_message)
# ---- Constantes de horario -----
TZ                 = ZoneInfo("America/Mexico_City")
INICIO_HORARIO: time    = time(7, 0)  # 07:00 AM
FIN_HORARIO: time       = time(15, 0) # 3:00 PM 

def safe_get(data, *keys):
    # Función auxiliar para navegar safely por diccionarios anidados
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
            data = data[key]
        else:
            return None
    return data

def unix_to_america(ts_raw: int) -> datetime:
    """
    Convierte un timestamp Unix a un objeto datetime en la zona horaria de América/México_City.
    """
    dt_local: datetime = datetime.fromtimestamp(ts_raw, tz=ZoneInfo("UTC")).astimezone(TZ)
    print("⏰ Hora local:", dt_local)
    return dt_local

def list_to_string(list, sep=", "):
    """
    Convierte una lista de cadenas en una sola cadena, uniendo los elementos con el separador especificado.
    """
    cleaned = (str(s).strip() for s in list)
    return sep.join(cleaned)

# --- Verifica si el timestamp está dentro del horario permitido ---
def esta_en_horario(ts_raw:int) -> bool:
    """ 
    Verifica si el mensaje fue enviado dentro del horario permitido 
    """
    dt_local: datetime  = datetime.fromtimestamp(ts_raw, tz=ZoneInfo("UTC")).astimezone(TZ)
    hora_actual         = dt_local.time()
    
    if hora_actual <= INICIO_HORARIO or hora_actual >= FIN_HORARIO:
        print(f"Fuera de horario: {hora_actual} no está entre {INICIO_HORARIO} y {FIN_HORARIO}")
        return False
    else:
        print(f"En horario: {hora_actual} está entre {INICIO_HORARIO} y {FIN_HORARIO}")
        return True

 # ---- Verificar si han pasado 8 horas desde el ultimo mensaje ----
def is_8_hours(wa_id: str) -> tuple[bool, str]:
    """
    Devuelve:
      (True,  "Usuario desbloqueado")  si la ventana ya expiró o nunca existió bloqueo.
      (False, "Usuario bloqueado…")    si sigue dentro de la ventana.
    """
    bloqueo_ts = get_bloqueo(wa_id)          # debería devolver int|None
    if bloqueo_ts is None:
        return True, "No hay bloqueo registrado"

    bloqueo_dt = unix_to_america(bloqueo_ts)
    desbloqueo = bloqueo_dt + timedelta(minutes=2) # Cambié de 8 horas a 2 minutos para pruebas
    dt_actual = datetime.now(tz=TZ)
    if dt_actual >= desbloqueo:
        #clear_user_state(wa_id)               
        return True, "Usuario desbloqueado"

    # Aún bloqueado → calculamos tiempo restante
    diferencia = desbloqueo - dt_actual
    total_segundos = int(diferencia.total_seconds())
    horas_restantes = total_segundos // 3600
    minutos_restantes = (total_segundos % 3600) // 60
    mensaje = (
        f"Usuario bloqueado. Desbloqueo en "
        f"{horas_restantes} horas y {minutos_restantes} minutos."
    )
    return False, mensaje

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def inactivity(wa_id) -> bool:
    """
    Determina si el usuario lleva más de X minutos inactivo.
    Si es así, reinicia los estados para que vuelva a empezar su flujo.
    """
    ultimo_mensaje_str: str = get_user_last_message(wa_id)
    if ultimo_mensaje_str is None:
        return False
    # Hora actual en TZ local
    ultimo_mensaje = datetime.strptime(ultimo_mensaje_str, "%Y-%m-%d %H:%M:%S.%f")
    hora_actual = datetime.now()
    
    diferencia = hora_actual - ultimo_mensaje

    print(f"Hora actual: {hora_actual}")
    print(f"Último mensaje: {ultimo_mensaje}")
    print(f"Diferencia: {diferencia} ({diferencia.total_seconds()/60:.2f} minutos)")

    if diferencia.total_seconds() >= 60 * 60:
        clear_user_state(wa_id)
        return True

    return False