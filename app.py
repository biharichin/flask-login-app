from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from dotenv import load_dotenv
import secrets
secrets.token_hex(16)
# Ensure the .env file is loaded to access environment variables
# This is necessary to keep sensitive information like database credentials secure.

# Load environment variables from .env file
load_dotenv()

# --- TEMPORARY DEBUGGING ---
# This block will help you check if your .env file is being loaded correctly.
# You can remove this code once you confirm everything is working.
print("--- Checking Environment Variables ---")
print(f"SECRET_KEY loaded: {'Yes' if os.environ.get('SECRET_KEY') else 'No, not found!'}")
print(f"DB_HOST loaded: {os.environ.get('DB_HOST')}")
print(f"ADMIN_EMAIL loaded: {os.environ.get('ADMIN_EMAIL')}")
print("------------------------------------")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Load configuration from environment variables
app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

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
        logging.error(f"Error adding city column: {e}")
        return "❌ An error occurred. Check server logs."


# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
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
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
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
                city VARCHAR(100),
                hospital_type VARCHAR(100),
                photo_url VARCHAR(255)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS pathology_labs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100),
                lab_type VARCHAR(100),
                photo_url VARCHAR(255),
                account_id INT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS hospital_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(512) NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS pathology_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(512) NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        return "✅ Tables created successfully!"
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        return "❌ An error occurred creating tables. Check server logs."

@app.route("/addphotocolumn")
def add_photo_column():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("ALTER TABLE doctors ADD COLUMN photo VARCHAR(255)")
        conn.commit()
        conn.close()
        return "✅ 'photo' column added to doctors table"
    except Exception as e:
        logging.error(f"Error adding photo column: {e}")
        return "❌ An error occurred. Check server logs."

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        # Storing the plain text password as requested
        password = request.form["password"]
        city = request.form["city"]

        conn = get_connection()
        c = conn.cursor()
        logging.info(f"Processing signup for user: {email}")
        # Store the hashed password, not the plain text one
        c.execute("INSERT INTO users (email, password, city) VALUES (%s, %s, %s)", (email, password, city))
        conn.commit()
        conn.close()
        flash("Signup successful! Please log in.", "success")
        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        # Use a dictionary cursor to access columns by name (e.g., user['password'])
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = c.fetchone()
        conn.close()

        # Check if a user was found and if the plain text password matches
        if user and user['password'] == password:
            # Set the session to log the user in
            session["email"] = user['email']
            return redirect("/dashboard")
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect("/login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    # Check if user is logged in
    email = session.get("email")  # Use .get() to safely access the email
    doctors = []
    hospitals = []
    pathology_labs = []
    conn = None
    try:
        conn = get_connection()
        # Use a dictionary cursor for easier access in the template (e.g., doctor.name)
        c = conn.cursor(dictionary=True)

        # Get 5 doctors for the dashboard
        c.execute("SELECT id, name, specialty, city, photo FROM doctors LIMIT 5")
        
        doctors = c.fetchall()

        # Get 5 hospitals for the dashboard
        c.execute("SELECT id, name, city, photo_url FROM hospitals LIMIT 5")
        
        hospitals = c.fetchall()

        # Get 5 pathology labs for the dashboard
        c.execute("SELECT id, name, city, photo_url FROM pathology_labs LIMIT 5")

        pathology_labs = c.fetchall()

    except Exception as e:
        flash("Error loading dashboard data. Please try again later.", "danger")
        logging.error(f"Dashboard loading error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("dashboard.html", email=email, doctors=doctors, hospitals=hospitals, pathology_labs=pathology_labs)

@app.route("/admin")
def admin():
    # Security check: Only allow the designated admin user
    if "email" not in session or session.get("email") != ADMIN_EMAIL:
        flash("You do not have permission to access this page.", "danger")
        return redirect("/dashboard") # Redirect non-admins to the dashboard
    conn = get_connection()
    c = conn.cursor(dictionary=True)

    # Users
    c.execute("SELECT email, city FROM users")
    users = c.fetchall()

    # Doctors
    c.execute("SELECT name, age, gender, specialty, city, photo FROM doctors")
    doctors = c.fetchall()

    # Hospitals with their account email
    c.execute("""
        SELECT
            h.name, h.city, h.hospital_type, ha.email
        FROM
            hospitals h
        LEFT JOIN
            hospital_accounts ha ON h.account_id = ha.id
    """)
    hospitals = c.fetchall()

    # Pathology Labs with their account email
    c.execute("""
        SELECT
            pl.name, pl.city, pl.lab_type, pa.email
        FROM
            pathology_labs pl
        LEFT JOIN
            pathology_accounts pa ON pl.account_id = pa.id
    """)
    pathology_labs = c.fetchall()

    conn.close()
    return render_template("admin.html", users=users, doctors=doctors, hospitals=hospitals, pathology_labs=pathology_labs)

@app.route("/doctor", methods=["GET"])
def doctor_search():
    if "email" not in session:
        return redirect("/login")
 
    # Get filter values from the request URL, stripping any extra whitespace
    city = request.args.get("city", "").strip()
    name = request.args.get("name", "").strip()
    specialty = request.args.get("specialty", "").strip()

    # Validation: If other fields are filled but city is not, show an error.
    if not city and (name or specialty):
        flash("first choose your city.", "warning")
        # Render the page with an empty result set, but keep the search terms in the form
        return render_template("doctor.html", results=[], search_terms={'city': city, 'name': name, 'specialty': specialty})

    results = []
    conn = None
    try:
        conn = get_connection()
        # Use a dictionary cursor for easier and more readable access in the template
        c = conn.cursor(dictionary=True)

        # If a city is provided, perform a filtered search.
        if city:
            # Start with a base query and a list for parameters
            query = "SELECT id, name, specialty, city, photo FROM doctors WHERE city LIKE %s"
            params = ['%' + city + '%']

            # Dynamically add conditions for optional filters
            if name:
                query += " AND name LIKE %s"
                params.append('%' + name + '%')

            if specialty:
                query += " AND specialty LIKE %s"
                params.append('%' + specialty + '%')

            c.execute(query, tuple(params))
        # Otherwise, if no filters are provided, show all doctors.
        else:
            c.execute("SELECT id, name, specialty, city, photo FROM doctors")
        
        results = c.fetchall()
    except Exception as e:
        flash("An error occurred while searching. Please try again.", "danger")
        logging.error(f"Doctor search error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    # Pass search terms back to the template to keep the form fields populated
    return render_template("doctor.html", results=results, search_terms={'city': city, 'name': name, 'specialty': specialty})

@app.route("/doctor_detail/<int:doctor_id>")
def doctor_detail(doctor_id):
    if "email" not in session:
        return redirect("/login")

    doctor = None
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        # Fetch all details for the specific doctor
        c.execute("SELECT name, age, gender, specialty, city, photo FROM doctors WHERE id = %s", (doctor_id,))
        doctor = c.fetchone()
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("doctor_detail.html", doctor=doctor)


@app.route("/hospital", methods=["GET"])
def hospital_page():
    if "email" not in session:
        return redirect("/login")

    city = request.args.get("city", "").strip()
    name = request.args.get("name", "").strip()
    hospital_type = request.args.get("hospital_type", "").strip()

    # Validation: If other fields are filled but city is not, show an error.
    if not city and (name or hospital_type):
        flash("first choose your city.", "warning")
        return render_template("hospital.html", results=[], search_terms={'city': city, 'name': name, 'hospital_type': hospital_type})

    results = []
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor(dictionary=True)

        # If a city is provided, perform a filtered search.
        if city:
            query = "SELECT id, name, city, hospital_type, photo_url FROM hospitals WHERE city LIKE %s"
            params = ['%' + city + '%']
            if name:
                query += " AND name LIKE %s"
                params.append('%' + name + '%')

            c.execute(query, tuple(params))
        # Otherwise, if no filters are provided, show all hospitals.
        else:
            c.execute("SELECT id, name, city, hospital_type, photo_url FROM hospitals")

        results = c.fetchall()
    except Exception as e:
        flash("An error occurred while searching. Please try again.", "danger")
        logging.error(f"Hospital search error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("hospital.html", results=results, search_terms={'city': city, 'name': name, 'hospital_type': hospital_type})

@app.route("/hospital_detail/<int:hospital_id>")
def hospital_detail(hospital_id):
    if "email" not in session:
        return redirect("/login")
    
    hospital = None
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT name, city, hospital_type, photo_url FROM hospitals WHERE id = %s", (hospital_id,))
        hospital = c.fetchone()
    finally:
        if conn and conn.is_connected():
            conn.close()
    return render_template("hospital_detail.html", hospital=hospital)

@app.route("/pathology_detail/<int:lab_id>")
def pathology_detail(lab_id):
    if "email" not in session:
        return redirect("/login")

    lab = None
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT name, city, lab_type, photo_url FROM pathology_labs WHERE id = %s", (lab_id,))
        lab = c.fetchone()
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("pathology_detail.html", lab=lab)

@app.route("/pathology", methods=["GET"])
def pathology_page():
    if "email" not in session:
        return redirect("/login")

    city = request.args.get("city", "").strip()
    name = request.args.get("name", "").strip()

    # If name is provided without a city, flash a warning message.
    if not city and name:
        flash("first choose your city.", "warning")
        return render_template("pathology.html", results=[], search_terms={'city': city, 'name': name})

    results = []
    conn = None
    try:
        conn = get_connection()
        c = conn.cursor(dictionary=True)

        # Build and execute the query based on provided filters.
        if city:
            query = "SELECT id, name, city, lab_type, photo_url FROM pathology_labs WHERE city LIKE %s"
            params = ['%' + city + '%']
            if name:
                query += " AND name LIKE %s"
                params.append('%' + name + '%')
            c.execute(query, tuple(params))
        else:  # If no filters (or just the city is empty), show all labs.
            c.execute("SELECT id, name, city, lab_type, photo_url FROM pathology_labs")
        
        results = c.fetchall()
    except Exception as e:
        flash("An error occurred while searching. Please try again.", "danger")
        logging.error(f"Pathology lab search error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template("pathology.html", results=results, search_terms={'city': city, 'name': name})

@app.route("/submit", methods=["GET", "POST"])
def submit_doctor():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        specialty = request.form["specialty"]
        city = request.form.get("city", "")  # Add city field
        photo = request.form.get("photo", "")  # Add photo field

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO doctors (name, age, gender, specialty, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                  (name, age, gender, specialty, city, photo))
        conn.commit()
        flash("Doctor submitted successfully!", "success")
        conn.close()
        return redirect("/dashboard") # Redirect to a relevant page
    return render_template("submit.html")

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


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    doctor_results = []
    hospital_results = []
    pathology_results = []

    return render_template(
        "search.html",
        doctor_results=doctor_results, hospital_results=hospital_results, pathology_results=pathology_results
    )
