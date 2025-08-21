import mysql.connector
from typing import Optional, List, Tuple, cast, Any
import os
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE"),
}

def set_user_state(wa_id: Optional[str], state: str):
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("REPLACE INTO user_states (wa_id, state) VALUES (%s, %s)", (wa_id, state))
    conn.commit()
    c.close()
    conn.close()

def get_user_state(wa_id: Optional[str]) -> Optional[str]:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("SELECT state FROM user_states WHERE wa_id = %s", (wa_id,))
    row: Any = cast(List[Tuple[str,str]],c.fetchone())
    c.close()
    conn.close()
    return row[0] if row else None

def clear_user_state(wa_id: Optional[str]) -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("DELETE FROM user_states WHERE wa_id = %s", (wa_id,))
    conn.commit()
    c.close()
    conn.close()

def print_all_user_states():
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute('SELECT wa_id, state FROM user_states')
    rows = cast(List[Tuple[str,str]],c.fetchall())
    c.close()
    conn.close()
    for row in rows:
        print(f"wa_id: {row[0]}, state: {row[1]}")