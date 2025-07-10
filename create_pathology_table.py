
import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create pathology table
c.execute("""
    CREATE TABLE IF NOT EXISTS pathology_labs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        type TEXT
    )
""")

# Check if already inserted
c.execute("SELECT COUNT(*) FROM pathology_labs")
count = c.fetchone()[0]

if count == 0:
    labs = [
        ("Red Cross Path Lab", "Delhi", "Blood Test"),
        ("HealthFirst Labs", "Mumbai", "Full Body Checkup"),
        ("Dr. Lal PathLabs", "Kolkata", "General Tests"),
        ("Apollo Diagnostics", "Hyderabad", "Advanced Diagnostics")
    ]
    c.executemany("INSERT INTO pathology_labs (name, city, type) VALUES (?, ?, ?)", labs)
    print("Pathology labs added.")
else:
    print("Labs already exist. Skipping...")

conn.commit()
conn.close()
# This script creates a new table called 'pathology_labs' in the existing 'users.db'
# database and inserts sample data if the table is empty. It includes columns for lab name,