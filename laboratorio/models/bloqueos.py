import mysql.connector
from typing import Optional
import os
import typing
from typing import cast, Tuple, List

DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE"),
}

def set_bloqueo(wa_id: Optional[str], desbloqueo_ts: int) -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO bloqueos (wa_id, desbloqueo_ts) VALUES (%s, %s)",
        (wa_id, desbloqueo_ts)
    )
    conn.commit()
    c.close()
    conn.close()

def get_bloqueo(wa_id: str) -> Optional[int]:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("SELECT desbloqueo_ts FROM bloqueos WHERE wa_id = %s", (wa_id,))
    row = cast(Optional[Tuple[str,str]],c.fetchone())
    c.close()
    conn.close()
    if row is None:
        return None
    return row[0]  # Aquí row[0] es un int porque desbloqueo_ts es BIGINT

def clear_bloqueo(wa_id: Optional[str]) -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("DELETE FROM bloqueos WHERE wa_id = %s", (wa_id,))
    conn.commit()
    c.close()
    conn.close()

def print_all_bloqueos() -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("SELECT wa_id, desbloqueo_ts FROM bloqueos")
    rows = cast(List[Tuple[str,str]], c.fetchall())
    c.close()
    conn.close()
    for row in rows:
        print(f"wa_id: {row[0]}, desbloqueo_ts: {row[1]}")