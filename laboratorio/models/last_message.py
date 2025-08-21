import mysql.connector
from typing import Optional, Any
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE"),
}

def set_user_last_message(wa_id: str) -> None:
    ts_str = datetime.now()
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO last_message (wa_id, timestamp) VALUES (%s, %s)",
        (wa_id, ts_str)
    )
    conn.commit()
    c.close()
    conn.close()

def get_user_last_message(wa_id: str) -> str | Any:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute(
        "SELECT timestamp FROM last_message WHERE wa_id = %s",
        (wa_id,)
    )
    row : Any = c.fetchone()
    c.close()
    conn.close()

    if row is None:
        return None
    return row[0]