
import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Keep only 1st 4 hospitals
c.execute("DELETE FROM hospitals WHERE id NOT IN (SELECT id FROM hospitals ORDER BY id LIMIT 4)")

# Keep only 1st 4 labs
c.execute("DELETE FROM pathology_labs WHERE id NOT IN (SELECT id FROM pathology_labs ORDER BY id LIMIT 4)")

conn.commit()
conn.close()

print("Duplicate data removed.")
# This script connects to the 'users.db' database and removes duplicate entries
# from the 'hospitals' and 'pathology_labs' tables, keeping only