
import sqlite3

# Connect to your existing users.db file
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create a new table for doctors
c.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        specialty TEXT
    )
""")

# Add some sample doctors
doctors = [
    ("Dr. Ramesh", 45, "Male", "Cardiology"),
    ("Dr. Anjali", 38, "Female", "Dermatology"),
    ("Dr. Amit", 50, "Male", "Neurology"),
    ("Dr. Priya", 42, "Female", "Pediatrics")
]

c.executemany("INSERT INTO doctors (name, age, gender, specialty) VALUES (?, ?, ?, ?)", doctors)

# Save and close
conn.commit()
conn.close()

print("Doctor table created and sample doctors added.")
# This script creates a new table called 'doctors' in the existing 'users.db' SQLite database.
# It includes columns for id, name