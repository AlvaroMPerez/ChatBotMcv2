import mysql.connector
import os
from dotenv import load_dotenv
from typing import Optional, List, Tuple, cast
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("HOST"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "database": os.getenv("DATABASE"),
}

def message_id_exist(message_id: str) -> bool:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute('SELECT 1 FROM received_messages WHERE id = %s', (message_id,))
    exist = c.fetchone() is not None
    c.close()
    conn.close()
    return exist

def save_message_id(message_id: str) -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute('INSERT INTO received_messages (id) VALUES (%s)', (message_id,))
    conn.commit()
    c.close()
    conn.close()

def print_all_messages_id() -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()  # cursor normal
    c.execute('SELECT id FROM received_messages')
    rows =cast(List[Tuple[str, int]], c.fetchall()) 
    c.close()
    conn.close()

    print("Saved Ids in database")
    for row in rows:
        print(row[0])