
import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create table for hospitals
c.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        type TEXT
    )
""")

# Add sample hospitals
hospitals = [
    ("City Care Hospital", "Delhi", "Multi-Specialty"),
    ("Sunrise Hospital", "Mumbai", "Cardiac"),
    ("Rainbow Children's Hospital", "Hyderabad", "Pediatrics"),
    ("Apollo Hospital", "Chennai", "General")
]

c.executemany("INSERT INTO hospitals (name, city, type) VALUES (?, ?, ?)", hospitals)

conn.commit()
conn.close()

print("Hospital table created and data added.")
# This script creates a new table called 'hospitals' in the existing 'users.db' SQLite database.
# It includes columns for id, name, city, and type of hospital.