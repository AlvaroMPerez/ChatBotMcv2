import sqlite3

def message_id_exist(message_id):
    conn = sqlite3.connect("recived_messages_ids.db")
    c = conn.cursor()
    c.execute('SELECT 1 FROM received_messages where id = ?', (message_id,))
    exist = c.fetchone() is not None
    conn.close()
    return exist

def save_message_id(message_id):
    conn = sqlite3.connect("recived_messages_ids.db")
    c = conn.cursor()
    c.execute('INSERT INTO received_messages (id) VALUES (?)', (message_id,))
    conn.commit()
    conn.close()


# Testing function for database
def print_all_messages_id():
    conn = sqlite3.connect("recived_messages_ids.db")
    c = conn.cursor()
    c.execute('SELECT id FROM received_messages')
    rows = c.fetchall()
    conn.close()

    print("Saved Ids in batabase")
    for row in rows:
        print(row[0])