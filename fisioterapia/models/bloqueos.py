import sqlite3

DB_PATH = "recived_messages_ids.db"

def set_bloqueo(wa_id: str, desbloqueo_ts: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO bloqueos (wa_id, desbloqueo_ts) VALUES (?, ?)", (wa_id, desbloqueo_ts))
    conn.commit()
    conn.close()

def get_bloqueo(wa_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT desbloqueo_ts FROM bloqueos WHERE wa_id = ?", (wa_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def clear_bloqueo(wa_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM bloqueos WHERE wa_id = ?", (wa_id,))
    conn.commit()
    conn.close()

def print_all_bloqueos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT wa_id, desbloqueo_ts FROM bloqueos')
    rows = c.fetchall()
    conn.close()
    for row in rows:
        print(f"wa_id: {row[0]}, desbloqueo_ts: {row[1]}")