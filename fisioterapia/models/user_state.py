import sqlite3

DB_PATH = "recived_messages_ids.db"

def set_user_state(wa_id : str,state : str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO user_states (wa_id, state) VALUES (?, ?)", (wa_id, state))
    conn.commit()
    conn.close()

def get_user_state(wa_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT state FROM user_states WHERE wa_id = ?", (wa_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def clear_user_state(wa_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM user_states WHERE wa_id = ?", (wa_id,))
    conn.commit()
    conn.close()

def print_all_user_states():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT wa_id, state FROM user_states')
    rows = c.fetchall()
    conn.close()
    for row in rows:
        print(f"wa_id: {row[0]}, state: {row[1]}")