import sqlite3

conn = sqlite3.connect("interview.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    subject TEXT,
    score INTEGER,
    percentage TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")