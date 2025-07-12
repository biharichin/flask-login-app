from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ✅ MySQL connection (inside app.py)
def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12789576",
        password="svgwzPG2NJ",
        database="sql12789576",
        port=3306
    )

# ✅ Home page
@app.route("/")
def home():
    if "user" in session:
        return render_template("dashboard.html")
    return render_template("home.html")

@app.route("/createtables")
def create_tables():
    try:
        conn = get_connection()
        c = conn.cursor()

        # Create users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(100),
                password VARCHAR(100),
                city VARCHAR(50)
            )
        """)

        # Create doctors table
        c.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                gender VARCHAR(10),
                specialty VARCHAR(100)
            )
        """)

        # Create hospitals table
        c.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100)
            )
        """)

        # Create pathology_labs table
        c.execute("""
            CREATE TABLE IF NOT EXISTS pathology_labs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100)
            )
        """)

        conn.commit()
        conn.close()
        return "✅ Tables created successfully!"
    except Exception as e:
        return f"❌ Error creating tables: {e}"

# ✅ Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        city = request.form["city"]

        conn = get_connection()
        c = conn.cursor(buffered=True)
        c.execute("INSERT INTO users (email, password, city) VALUES (%s, %s, %s)", (email, password, city))
        conn.commit()
        conn.close()
        return "Signup successful! Go to /login"

    return render_template("signup.html")

# ✅ Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        c = conn.cursor(buffered=True)
        c.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "Invalid email or password"

    return render_template("login.html")

# ✅ Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ✅ Admin Page
@app.route("/admin")
def admin():
    conn = get_connection()
    c = conn.cursor(buffered=True)
    c.execute("SELECT email, password, city FROM users")
    users = c.fetchall()
    conn.close()
    return render_template("admin.html", users=users)

# ✅ Doctor Search Page
@app.route("/doctor", methods=["GET"])
def doctor_search():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()
    if query:
        c.execute("SELECT name, age, gender, specialty FROM doctors WHERE name LIKE %s OR specialty LIKE %s",
                  (f"%{query}%", f"%{query}%"))
    else:
        c.execute("SELECT name, age, gender, specialty FROM doctors")
    results = c.fetchall()
    conn.close()
    return render_template("doctor.html", results=results)

# ✅ Hospital Page
@app.route("/hospital", methods=["GET"])
def hospital_page():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()
    if query:
        c.execute("SELECT name, city FROM hospitals WHERE name LIKE %s OR city LIKE %s",
                  (f"%{query}%", f"%{query}%"))
    else:
        c.execute("SELECT name, city FROM hospitals")
    hospitals = c.fetchall()
    conn.close()
    return render_template("hospital.html", hospitals=hospitals)

# ✅ Pathology Lab Page
@app.route("/pathology", methods=["GET"])
def pathology_page():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()
    if query:
        c.execute("SELECT name, city FROM pathology_labs WHERE name LIKE %s OR city LIKE %s",
                  (f"%{query}%", f"%{query}%"))
    else:
        c.execute("SELECT name, city FROM pathology_labs")
    labs = c.fetchall()
    conn.close()
    return render_template("pathology.html", labs=labs)

# ✅ Doctor Plus App: Add Doctor Form
@app.route("/submit", methods=["POST", "GET"])
def submit_doctor():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        specialty = request.form["specialty"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO doctors (name, age, gender, specialty) VALUES (%s, %s, %s, %s)",
                  (name, age, gender, specialty))
        conn.commit()
        conn.close()
        return "Doctor added successfully!"

    return render_template("submit.html")

# ✅ Global Search: Navbar
@app.route("/search", methods=["GET"])
def global_search():
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT name FROM doctors WHERE name LIKE %s OR specialty LIKE %s",
              (f"%{query}%", f"%{query}%"))
    doctors = c.fetchall()

    c.execute("SELECT name FROM hospitals WHERE name LIKE %s OR city LIKE %s",
              (f"%{query}%", f"%{query}%"))
    hospitals = c.fetchall()

    c.execute("SELECT name FROM pathology_labs WHERE name LIKE %s OR city LIKE %s",
              (f"%{query}%", f"%{query}%"))
    labs = c.fetchall()

    conn.close()
    return render_template("search.html", doctors=doctors, hospitals=hospitals, labs=labs, query=query)

# ✅ For Render Hosting
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
