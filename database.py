import sqlite3
from datetime import datetime

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Table 1: Users
    cursor.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT NOT NULL)')
    # Table 2: History (New!)
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                      (email TEXT, original TEXT, translated TEXT, direction TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def add_user(email, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def verify_user(email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# --- NEW FUNCTIONS FOR HISTORY ---
def save_history(email, original, translated, direction):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?)', (email, original, translated, direction, now))
    conn.commit()
    conn.close()

def get_history(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original, translated, direction, timestamp FROM history WHERE email=? ORDER BY timestamp DESC', (email,))
    rows = cursor.fetchall()
    conn.close()
    return rows