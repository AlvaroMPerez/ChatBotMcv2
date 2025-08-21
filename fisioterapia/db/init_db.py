import sqlite3


def init_db():
    conn = sqlite3.connect("recived_messages_ids.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS received_messages (
            id TEXT PRIMARY KEY,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
              wa_id TEXT PRIMARY KEY,
              state TEXT)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueos(
            wa_id TEXT PRIMARY KEY,
            desbloqueo_ts INTEGER
)          
    ''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")