from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
@app.route("/addcitycolumn")
def add_city_column():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("ALTER TABLE users ADD COLUMN city VARCHAR(50)")
        conn.commit()
        conn.close()
        return "✅ 'city' column added to users table"
    except Exception as e:
        return f"❌ Error: {e}"


# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12789576",
        password="svgwzPG2NJ",
        database="sql12789576",
        port=3306
    )

@app.route("/")
def home():
    # Redirect the root URL to the main dashboard for consistency
    return redirect("/dashboard")

@app.route("/createtables")
def create_tables():
    try:
        conn = get_connection()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(100),
                password VARCHAR(100),
                city VARCHAR(50)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                gender VARCHAR(10),
                specialty VARCHAR(100),
                city VARCHAR(100)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100)
            )
        """)

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

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        city = request.form["city"]

        conn = get_connection()
        c = conn.cursor()
        print("🟢 Connected and inserting data")
        c.execute("INSERT INTO users (email, password, city) VALUES (%s, %s, %s)", (email, password, city))
        conn.commit()
        conn.close()
        return "Signup successful! Go to /login"
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["email"] = email
            return redirect("/dashboard")
        else:
            return "Invalid credentials. Try again."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    # Check if user is logged in to provide a personalized experience
    email = session.get("email")  # Use .get() to safely access the email
    return render_template("dashboard.html", email=email)

@app.route("/admin")
def admin():
    if "email" not in session:
        return redirect("/login")
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("SELECT email, password, city FROM users")
    users = c.fetchall()

    # Doctors
    c.execute("SELECT name, age, gender, specialty, city FROM doctors")
    doctors = c.fetchall()

    conn.close()
    return render_template("admin.html", users=users, doctors=doctors)

@app.route("/doctor", methods=["GET"])
def doctor_search():
    if "email" not in session:
        return redirect("/login")

    city = request.args.get("city", "")
    disease = request.args.get("disease", "")
    conn = get_connection()
    c = conn.cursor()
    if city and disease:
        c.execute(
            "SELECT name, age, gender, specialty, city, photo FROM doctors WHERE city LIKE %s AND specialty LIKE %s",
            ('%' + city + '%', '%' + disease + '%')
        )
    else:
        c.execute("SELECT name, age, gender, specialty, city, photo FROM doctors")
    results = c.fetchall()
    conn.close()
    return render_template("doctor.html", results=results)


@app.route("/hospital", methods=["GET"])
def hospital_page():
    if "email" not in session:
        return redirect("/login")
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()
    if query:
        c.execute("SELECT name, city FROM hospitals WHERE name LIKE %s OR city LIKE %s", 
                  ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute("SELECT name, city FROM hospitals")
    results = c.fetchall()
    conn.close()
    return render_template("hospital.html", results=results)

@app.route("/pathology", methods=["GET"])
def pathology_page():
    if "email" not in session:
        return redirect("/login")
    query = request.args.get("query", "")
    conn = get_connection()
    c = conn.cursor()
    if query:
        c.execute("SELECT name, city FROM pathology_labs WHERE name LIKE %s OR city LIKE %s", 
                  ('%' + query + '%', '%' + query + '%'))
    else:
        c.execute("SELECT name, city FROM pathology_labs")
    results = c.fetchall()
    conn.close()
    return render_template("pathology.html", results=results)

@app.route("/submit", methods=["GET", "POST"])
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

@app.route("/fixcity")
def fix_city_column():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("ALTER TABLE users ADD COLUMN city VARCHAR(50)")
        conn.commit()
        conn.close()
        return "✅ City column added"
    except Exception as e:
        return f"❌ Error: {e}"
#app.route("/viewusers")
@app.route("/dbcheck")
def db_check():
    try:
        conn = get_connection()
        if conn.is_connected():
            return "🟢 App is using MySQL!"
        else:
            return "🔴 Not connected to MySQL."
    except Exception as e:
        return f"❌ Error: {e}"

# For Render.com hosting
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
