import sqlite3

def init_db():
    with sqlite3.connect('assistant/jarvis.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                _id INTEGER PRIMARY KEY,
                input TEXT,
                output TEXT,
                _inserted_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def insert_conversation(input, output):
    with sqlite3.connect('assistant/jarvis.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_history (input, output) 
            VALUES (?, ?)
        ''', (input, output))
        conn.commit()

def fetch_all_conversations(limit=None):
    with sqlite3.connect('assistant/jarvis.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT _id, input, output, _inserted_timestamp 
            FROM conversation_history
        ''')
        rows = cursor.fetchall()
        if limit:
            return rows[:limit]
        return rows
