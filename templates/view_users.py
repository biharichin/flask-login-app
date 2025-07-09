import sqlite3

# Step 1: Connect to the database file
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Step 2: Run SQL to get all users
cursor.execute("SELECT * FROM users")

# Step 3: Fetch and print each user
users = cursor.fetchall()

print("All users signed up:")
for user in users:
    print(f"- Email: {user[1]}, Password: {user[2]}")

conn.close()
