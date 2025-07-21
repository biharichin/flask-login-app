from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from dotenv import load_dotenv
from db import get_db, close_db # Import the new db functions
# Ensure the .env file is loaded to access environment variables
# This is necessary to keep sensitive information like database credentials secure.

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

app = Flask(__name__)
# Load configuration from environment variables
app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

# Register the close_db function to be called when the app context ends
app.teardown_appcontext(close_db)

@app.route("/")
def home():
    # Redirect the root URL to the main dashboard for consistency
    return redirect("/dashboard")

@app.route("/createtables")
def create_tables():
    try:
        conn = get_db()
        c = conn.cursor()

        logging.info("Attempting to create 'users' table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(512) NOT NULL,
                city VARCHAR(50)
            )
        """)
        logging.info("'users' table creation statement executed.")

        logging.info("Attempting to create 'doctors' table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                gender VARCHAR(10),
                specialty VARCHAR(100),
                city VARCHAR(100),
                photo VARCHAR(255)
            )
        """)
        logging.info("'doctors' table creation statement executed.")

        logging.info("Attempting to create 'hospitals' table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                city VARCHAR(100),
                hospital_type VARCHAR(100),
                photo_url VARCHAR(255),
                account_id INT
            )
        """)
        logging.info("'hospitals' table creation statement executed.")

        logging.info("Attempting to create 'pathology_labs' table...")
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
        logging.info("'pathology_labs' table creation statement executed.")

        logging.info("Attempting to create 'hospital_accounts' table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS hospital_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(512) NOT NULL
            )
        """)
        logging.info("'hospital_accounts' table creation statement executed.")

        logging.info("Attempting to create 'pathology_accounts' table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS pathology_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(512) NOT NULL
            )
        """)
        logging.info("'pathology_accounts' table creation statement executed.")

        conn.commit()
        logging.info("Database commit successful.")

        # Verify if 'users' table exists
        c.execute("SHOW TABLES LIKE 'users'")
        if c.fetchone():
            logging.info("'users' table verified to exist.")
        else:
            logging.warning("'users' table does NOT exist after creation attempt.")

        return "✅ Tables created successfully!"
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        return "❌ An error occurred creating tables. Check server logs."

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        city = request.form["city"]

        conn = get_db()
        c = conn.cursor()
        logging.info(f"Processing signup for user: {email}")
        logging.info(f"Signup function connected to database: {conn.database}")
        # Hash the password for security before storing it
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (email, password, city) VALUES (%s, %s, %s)", (email, hashed_password, city))
        conn.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        # Use a dictionary cursor to access columns by name (e.g., user['password'])
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = c.fetchone()

        # Check if a user was found and if the provided password matches the stored hash
        if user and check_password_hash(user['password'], password):
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
    try:
        conn = get_db()
        # Use a dictionary cursor for easier access in the template (e.g., doctor.name)
        c = conn.cursor(dictionary=True)

        # Get 5 doctors for the dashboard
        c.execute("SELECT id, name, specialty, city, photo FROM doctors WHERE photo IS NOT NULL AND photo != '' LIMIT 5")
        
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

    return render_template("dashboard.html", email=email, doctors=doctors, hospitals=hospitals, pathology_labs=pathology_labs)

@app.route("/admin")
def admin():
    # Security check: Only allow the designated admin user
    if "email" not in session or session.get("email") != ADMIN_EMAIL:
        flash("You do not have permission to access this page.", "danger")
        return redirect("/dashboard") # Redirect non-admins to the dashboard
    conn = get_db()
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

    return render_template("admin.html", users=users, doctors=doctors, hospitals=hospitals, pathology_labs=pathology_labs)

@app.route("/doctor", methods=["GET"])
def doctor_page():
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
    try:
        conn = get_db()
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

    # Pass search terms back to the template to keep the form fields populated
    return render_template("doctor.html", results=results, search_terms={'city': city, 'name': name, 'specialty': specialty})

@app.route("/doctor_detail/<int:doctor_id>")
def doctor_detail(doctor_id):
    if "email" not in session:
        return redirect("/login")

    doctor = None
    try:
        conn = get_db()
        c = conn.cursor(dictionary=True)
        # Fetch all details for the specific doctor
        c.execute("SELECT name, age, gender, specialty, city, photo FROM doctors WHERE id = %s", (doctor_id,))
        doctor = c.fetchone()
    except Exception as e:
        flash("An error occurred while fetching doctor details.", "danger")
        logging.error(f"Doctor detail error for id {doctor_id}: {e}")
        return redirect("/doctor") # Redirect back to the search page on error

    if not doctor:
        flash(f"Doctor with ID {doctor_id} not found.", "warning")
        return redirect("/doctor")

    return render_template("doctor_detail.html", doctor=doctor)


@app.route("/hospital", methods=["GET"])
def hospital_page():
    if "email" not in session:
        return redirect("/login")

    city = request.args.get("city", "").strip() 
    name = request.args.get("name", "").strip() 

    # If name is provided without a city, flash a warning message.
    if not city and name:
        flash("first choose your city.", "warning") 
        return render_template("hospital.html", results=[], search_terms={'city': city, 'name': name})

    results = []
    try:
        conn = get_db()
        c = conn.cursor(dictionary=True)

        # Build and execute the query based on provided filters.
        if city:
            query = "SELECT id, name, city, hospital_type, photo_url FROM hospitals WHERE city LIKE %s"
            params = ['%' + city + '%']
            if name:
                query += " AND name LIKE %s"
                params.append('%' + name + '%')
            c.execute(query, tuple(params))
        else:  # If no filters (or just the city is empty), show all hospitals.
            c.execute("SELECT id, name, city, hospital_type, photo_url FROM hospitals")

        results = c.fetchall()
    except Exception as e:
        flash("An error occurred while searching. Please try again.", "danger")
        logging.error(f"Hospital search error: {e}")

    return render_template("hospital.html", results=results, search_terms={'city': city, 'name': name})



@app.route("/hospital_detail/<int:hospital_id>")
def hospital_detail(hospital_id):
    if "email" not in session:
        return redirect("/login")
    
    hospital = None
    try:
        conn = get_db()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT name, city, hospital_type, photo_url FROM hospitals WHERE id = %s", (hospital_id,))
        hospital = c.fetchone()
    except Exception as e:
        flash("An error occurred while fetching hospital details.", "danger")
        logging.error(f"Hospital detail error for id {hospital_id}: {e}")
        return redirect("/hospital")

    if not hospital:
        flash(f"Hospital with ID {hospital_id} not found.", "warning")
        return redirect("/hospital")
    return render_template("hospital_detail.html", hospital=hospital)


@app.route("/pathology_detail/<int:lab_id>")
def pathology_detail(lab_id):
    if "email" not in session:
        return redirect("/login")

    lab = None
    try:
        conn = get_db()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT name, city, lab_type, photo_url FROM pathology_labs WHERE id = %s", (lab_id,))
        lab = c.fetchone()
    except Exception as e:
        flash("An error occurred while fetching pathology lab details.", "danger")
        logging.error(f"Pathology lab detail error for id {lab_id}: {e}")
        return redirect("/pathology")

    if not lab:
        flash(f"Pathology lab with ID {lab_id} not found.", "warning")
        return redirect("/pathology")

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
    try:
        conn = get_db()
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

    return render_template("pathology.html", results=results, search_terms={'city': city, 'name': name})

@app.route("/submit", methods=["GET", "POST"])
def submit_doctor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_str = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        specialty = request.form.get("specialty", "").strip()
        city = request.form.get("city", "")  # Add city field
        photo = request.form.get("photo", "")  # Add photo field

        # --- Basic Validation ---
        if not all([name, age_str, gender, specialty, city]):
            flash("All fields are required.", "danger")
            return render_template("submit.html", form_data=request.form)
        
        try:
            age = int(age_str)
        except ValueError:
            flash("Age must be a valid number.", "danger")
            return render_template("submit.html", form_data=request.form)

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO doctors (name, age, gender, specialty, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                  (name, age, gender, specialty, city, photo))
        conn.commit()
        flash("Doctor submitted successfully!", "success")
        return redirect("/dashboard") # Redirect to a relevant page
    return render_template("submit.html")

#app.route("/viewusers")
@app.route("/dbcheck")
def db_check():
    try:
        conn = get_db()
        if conn.is_connected():
            return "🟢 App is using MySQL!"
        else:
            return "🔴 Not connected to MySQL."
    except Exception as e:
        return f"❌ Error: {e}"

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    doctor_results = []
    hospital_results = []
    pathology_results = []

    if query:  # Only perform a search if a query is provided
        try:
            conn = get_db()
            c = conn.cursor(dictionary=True)
            search_term = f"%{query}%"

            # Search doctors by name or specialty
            c.execute("SELECT id, name, specialty, city, photo FROM doctors WHERE name LIKE %s OR specialty LIKE %s", (search_term, search_term))
            doctor_results = c.fetchall()

            # Search hospitals by name or type
            c.execute("SELECT id, name, city, hospital_type, photo_url FROM hospitals WHERE name LIKE %s OR hospital_type LIKE %s", (search_term, search_term))
            hospital_results = c.fetchall()

            # Search pathology labs by name or type
            c.execute("SELECT id, name, city, lab_type, photo_url FROM pathology_labs WHERE name LIKE %s OR lab_type LIKE %s", (search_term, search_term))
            pathology_results = c.fetchall()
        except Exception as e:
            flash("An error occurred during the search.", "danger")
            logging.error(f"Global search error for query '{query}': {e}")

    return render_template(
        "search.html",
        query=query,
        doctor_results=doctor_results, hospital_results=hospital_results, pathology_results=pathology_results
    )

# The app.run() block should be the very last thing in your file.
# This ensures that all routes are registered before the server starts.
# The `if __name__ == '__main__':` block is standard practice and ensures
# that the server only runs when the script is executed directly (e.g., `python app.py`),
# not when it's imported by another module (like a WSGI server like Gunicorn).
if __name__ == '__main__':
    # For Render.com hosting, the port is set via an environment variable.
    # Default to 5000 for local development.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True provides detailed error pages
