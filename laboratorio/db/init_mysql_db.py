import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def init_db():

    # Configura tu conexión
    conn = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE")
    )


    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS received_messages (
            id VARCHAR(255) PRIMARY KEY,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
            wa_id VARCHAR(14) PRIMARY KEY,
            state VARCHAR(255)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bloqueos (
            wa_id VARCHAR(255) PRIMARY KEY,
            desbloqueo_ts BIGINT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS last_message (
            wa_id varchar(255) PRIMARY KEY,
            timestamp VARCHAR(255)
        )
    ''')

    conn.commit()
    c.close()
    conn.close()
    print("Base de datos MySQL inicializada correctamente.")