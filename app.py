
from flask import Flask, render_template, request, redirect
import sqlite3
import os
import mysql.connector

app = Flask(__name__)
def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12789576",
        password="svgwzPG2NJ",
        database="sql12789576",
        port=3306
    )
# Initialize MySQL connection
# ✅ STEP 1: Create users.db file + users table if not exists
def init_db():
    if not os.path.exists("users.db"):
        conn = get_connection()
        c = conn.cursor(buffered=True)
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

        conn = get_connection()
        c = conn.cursor(buffered=True)
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

        conn = get_connection()
        c = conn.cursor(buffered=True)
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            return render_template("dashboard.html", email=email)
        else:
            return "Invalid email or password"
    return render_template("login.html")

# 🏢 ADMIN DASHBOARD
@app.route("/admin")
def admin():
    conn = get_connection()
    c = conn.cursor(buffered=True)

    # Get signed up users
    c.execute("SELECT email, password, city FROM users")
    users = c.fetchall()

    # Get doctors from doctor_plus_app
    c.execute("SELECT name, age, gender, specialty FROM doctors")
    doctors = c.fetchall()

    conn.close()
    return render_template("admin.html", users=users, doctors=doctors)


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
#doctor search
# 🏥 DOCTOR SEARCH PAGE
@app.route("/doctor", methods=["GET"])
def doctor_search():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor(buffered=True)

    if query:
        c.execute("SELECT name, age, gender, specialty FROM doctors WHERE name LIKE ? OR specialty LIKE ?", 
                  ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute("SELECT name, age, gender, specialty FROM doctors")

    results = c.fetchall()
    conn.close()

    return render_template("doctor.html", results=results)

# 🏥 DOCTOR TABLE CREATION
#hospital search
@app.route("/hospital")
def hospital_list():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor(buffered=True)

    if query:
        c.execute("SELECT name, city, type FROM hospitals WHERE name LIKE ? OR city LIKE ?", 
                  ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute("SELECT name, city, type FROM hospitals")

    results = c.fetchall()
    conn.close()
    return render_template("hospital.html", results=results)
# 🏥 HOSPITAL TABLE CREATION
# 🏥 HOSPITAL SEARCH PAGE
@app.route("/search")
def search_all():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor(buffered=True)

    # Search doctors
    c.execute("SELECT name, age, gender, specialty FROM doctors WHERE name LIKE ? OR specialty LIKE ?", 
              ('%' + query + '%', '%' + query + '%'))
    doctor_results = c.fetchall()

    # Search hospitals
    c.execute("SELECT name, city, type FROM hospitals WHERE name LIKE ? OR city LIKE ?", 
              ('%' + query + '%', '%' + query + '%'))
    hospital_results = c.fetchall()
    # Search pathology labs
# Search pathology labs
    c.execute("SELECT name, city, type FROM pathology_labs WHERE name LIKE ? OR city LIKE ?", 
          ('%' + query + '%', '%' + query + '%'))
    pathology_results = c.fetchall()

    conn.close()

    return render_template("search.html", doctor_results=doctor_results, hospital_results=hospital_results, pathology_results=pathology_results)
# 🏥 PATHOLOGY LABS PAGE
@app.route("/pathology")
def pathology_list():
    conn = get_connection()
    c = conn.cursor(buffered=True)
    c.execute("SELECT name, city, type FROM pathology_labs")
    results = c.fetchall()
    conn.close()
    return render_template("pathology.html", results=results)
# 🏥 PATHOLOGY LABS PAGE
@app.route("/testdb")
def testdb():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT DATABASE();")
        db = c.fetchone()
        conn.close()
        return f"✅ Connected to database: {db[0]}"
    except Exception as e:
        return f"❌ Error connecting to database: {e}"

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # For local development, you can use app.run(debug=True) to enable debug mode
    # Uncomment the line below for local development
    app.run(debug=True)
