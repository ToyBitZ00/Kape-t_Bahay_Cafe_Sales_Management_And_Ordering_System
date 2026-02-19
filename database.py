import sqlite3

def create_connection():
    conn = sqlite3.connect("kape't_bahay.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()