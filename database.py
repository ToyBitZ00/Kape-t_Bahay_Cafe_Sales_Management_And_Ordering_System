import sqlite3
import hashlib

def create_connection():
    conn = sqlite3.connect("kape't_bahay_database.db")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


#def create_tables():
#    conn = create_connection()
#    cursor = conn.cursor()
#    cursor.execute("""
#        CREATE TABLE IF NOT EXISTS users (
#            id INTEGER PRIMARY KEY AUTOINCREMENT,
#            username TEXT NOT NULL UNIQUE,
#            password TEXT NOT NULL,
#            role TEXT NOT NULL
#       )
#    """)
#   conn.commit()
#   conn.close()


#def delete_tables():
#    conn = create_connection()
#    cursor = conn.cursor()
#    cursor.execute("DROP TABLE IF EXISTS users")
#    conn.commit()
#    conn.close()




def add_user(username, password, role):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_pw, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()




def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users
    WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    return user




def verify_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    cursor.execute("""SELECT user_id, username, password, role 
                    FROM users 
                    WHERE username=? AND password=?""",
        (username, hashed_pw)
    )

    user = cursor.fetchone()
    conn.close()

    return user




