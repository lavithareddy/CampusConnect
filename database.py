import sqlite3

conn = sqlite3.connect("campusconnect.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS forms(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_type TEXT,
    description TEXT,
    status TEXT DEFAULT 'Pending'
)
""")
conn.commit()
conn.close()

print("Database Created Successfully!")