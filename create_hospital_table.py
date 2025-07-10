
import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create hospital table
c.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        type TEXT
    )
""")

# Only add sample hospitals if table is empty
c.execute("SELECT COUNT(*) FROM hospitals")
count = c.fetchone()[0]

if count == 0:
    hospitals = [
        ("AIIMS", "Delhi", "Multispecialty"),
        ("Apollo", "Hyderabad", "Cardiac"),
        ("Rainbow", "Delhi", "Child Specialist"),
        ("Fortis", "Mumbai", "General")
    ]
    c.executemany("INSERT INTO hospitals (name, city, type) VALUES (?, ?, ?)", hospitals)
    print("Hospitals added.")
else:
    print("Hospitals already exist. Skipping...")

conn.commit()
conn.close()
# This script creates a new table called 'hospitals' in the existing 'users.db