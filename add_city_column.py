
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Add city column (if it doesn't exist)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN city TEXT DEFAULT ''")
    print("✅ City column added successfully!")
except Exception as e:
    print("⚠️ Might already exist:", e)

conn.commit()
conn.close()
# This script adds a new column 'city' to the 'users' table in the SQLite database.
# If the column already exists, it will catch the exception and print a warning.