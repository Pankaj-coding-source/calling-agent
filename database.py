import sqlite3

def init_db():
    conn = sqlite3.connect('farmers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            language_code TEXT,
            crop TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_farmer_by_phone(phone):
    conn = sqlite3.connect('farmers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, language_code, crop FROM farmers WHERE phone=?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": row[0], "language_code": row[1], "crop": row[2]}
    return None