
from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ✅ STEP 1: Create users.db file + users table if not exists
def init_db():
    if not os.path.exists("users.db"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

init_db()  # 🚀 This runs once to create everything

# 📝 SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        city = request.form["city"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password, city) VALUES (?, ?, ?)", (email, password, city))
        conn.commit()
        conn.close()

        return ''' 
            <h3>Signup successful!</h3>
            <p>Go to <a href="/login">Login</a></p> '''
    return render_template("signup.html")

# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            return render_template("dashboard.html", email=email)
        else:
            return "Invalid email or password"
    return render_template("login.html")

# 🧑‍💼 ADMIN PAGE
@app.route("/admin")
def admin():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT email, password, city FROM users")
    users = c.fetchall()
    conn.close()
    return render_template("admin.html", users=users)

# 🏠 HOME
@app.route("/")
def home():
    return """
    <h1>Welcome!</h1>
    <p>Go to:
        <a href="/signup">Signup</a> |
        <a href="/login">Login</a> |
        <a href="/admin">Admin</a>
    </p>
    """
# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # For local development, you can use app.run(debug=True) to enable debug mode
    # Uncomment the line below for local development
    app.run(debug=True)
