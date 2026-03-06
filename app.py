# ==========================================
# HostelTrackerERP Flask App
# ------------------------------------------
# Author: You
# Description: This app handles authentication and CRUD operations
#              for students, rooms, allocations, payments, and maintenance.
# ==========================================
# ==========================================
# Importing Required Libraries and Modules
# ==========================================

# Flask core modules for building web applications
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
# Flask → main framework for creating the web app
# request → handles data sent from the frontend (like forms or JSON)
# jsonify → converts Python data into JSON format for API responses
# render_template → displays HTML pages stored in the 'templates' folder
# redirect → sends users to another route or page
# url_for → helps generate dynamic URLs for routes
# session → stores user data temporarily during a login session
# flash → sends one-time messages to users (e.g., “Login successful”)
# send_file → allows sending files (like PDFs or images) from the server to the browser

# CORS (Cross-Origin Resource Sharing) allows the frontend (e.g., JavaScript) 
# to communicate with the Flask backend, even if they are on different domains or ports
from flask_cors import CORS

# pyodbc is a Python library that lets your app connect and run SQL queries 
# on Microsoft SQL Server databases
import psycopg2  # PostgreSQL adapter for Python (use psycopg2 for PostgreSQL databases)

# os provides access to environment variables and operating system features
# (useful for reading sensitive information like database credentials)
import os

# dotenv lets you load environment variables from a '.env' file 
# so you don’t expose passwords or connection strings in your code
from dotenv import load_dotenv

# BytesIO allows handling files or binary data (like PDFs) directly in memory 
# instead of saving them temporarily to disk
from io import BytesIO

# reportlab is used to generate PDF documents programmatically
# letter defines the paper size (8.5 x 11 inches)
from reportlab.lib.pagesizes import letter  # type: ignore

# canvas provides functions to draw text, shapes, and images on the PDF
from reportlab.pdfgen import canvas  # type: ignore

# random is used to generate random numbers or selections — 
# useful for generating unique IDs, codes, or filenames
import random

# string gives access to string constants (like uppercase letters or digits)
# often used together with random to generate random strings or passwords
import string

# Load environment variables from .env file
load_dotenv()


def _generate_receipt_no(length: int = 8) -> str:
    """e.g. 069A8C18 — uppercase letters + digits, fixed length"""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=length))

def _get_unique_receipt_no(cursor, max_attempts: int = 5) -> str:
    """Try a few times to avoid collisions (DB also has UNIQUE constraint)."""
    for _ in range(max_attempts):
        candidate = _generate_receipt_no()
        cursor.execute("SELECT 1 FROM Payments WHERE receipt_no = %s", (candidate,))
        if not cursor.fetchone():
            return candidate
    raise Exception("Could not generate a unique receipt number after several attempts")





# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Secret key for sessions (should be set in .env for production)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')


# ============================
#   DATABASE CONNECTION SETUP
# ============================
def get_db_connection():
    # We will put Render's Internal Database URL into this environment variable later
    database_url = os.getenv('DATABASE_URL')
    
    # If working locally without the URL, print a warning
    if not database_url:
        raise ValueError("No DATABASE_URL set for Flask application")
        
    return psycopg2.connect(database_url)

# ============================
#         AUTHENTICATION
# ============================

@app.route('/api/dashboard')
def dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Rooms")
    room_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Allocations")
    allocation_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Payments")
    payment_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Maintenance")
    maintenance_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return jsonify({
        "students": student_count,
        "rooms": room_count,
        "allocations": allocation_count,
        "payments": payment_count,
        "maintenance": maintenance_count
    })



@app.route('/')
def index():
    if session.get('admin_logged_in'):
        return redirect(url_for('home_page'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, password FROM Admins WHERE username = %s AND password = %s", 
            (username, password)
        )
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            session['admin'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# ==================================
#    LOGIN REQUIRED DECORATOR
# ==================================
def login_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapped_view(**kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return view_func(**kwargs)
    return wrapped_view

# ==========================
#       HTML ROUTES
# ==========================
@app.route('/home')
@login_required
def home_page():
    return render_template('index.html')


@app.route('/students')
@login_required
def students_page():
    return render_template('students.html')

@app.route('/rooms')
@login_required
def rooms_page():
    return render_template('rooms.html')

@app.route('/allocations')
@login_required
def allocations_page():
    return render_template('allocations.html')

@app.route('/payments')
@login_required
def payments_page():
    return render_template('payments.html')

@app.route('/maintenance')
@login_required
def maintenance_page():
    return render_template('maintenance.html')

# ==========================
#       API ENDPOINTS
# ==========================
# -------- Students CRUD --------
@app.route('/students', methods=['GET'])
@login_required
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, matric_number, department, level, gender FROM Students")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    students = [{
        'student_id': r[0], 'name': r[1], 'matric_number': r[2],
        'department': r[3], 'level': r[4], 'gender': r[5]
    } for r in rows]
    return jsonify(students)

@app.route('/students', methods=['POST'])
@login_required
def add_student():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Students (name, matric_number, department, level, gender) VALUES (%s, %s, %s, %s, %s)",
        (data['name'], data['matric_number'], data['department'], data['level'], data['gender'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student added successfully'})

@app.route('/students/<int:student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Students SET name=%s, matric_number=%s, department=%s, level=%s, gender=%s WHERE student_id=%s",
        (data['name'], data['matric_number'], data['department'], data['level'], data['gender'], student_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student updated successfully'})

@app.route('/students/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE student_id=%s", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student deleted successfully'})

# -------- Rooms CRUD --------
@app.route('/rooms', methods=['GET'])
@login_required
def get_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rooms")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    rooms = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    return jsonify(rooms)

@app.route('/rooms', methods=['POST'])
@login_required
def add_room():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Rooms (hostel_name, room_number, capacity, current_occupants) VALUES (%s, %s, %s, %s)",
        (data['hostel_name'], data['room_number'], data['capacity'], data['current_occupants'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room added successfully'})

@app.route('/rooms/<int:room_id>', methods=['PUT'])
@login_required
def update_room(room_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Rooms SET hostel_name=%s, room_number=%s, capacity=%s, current_occupants=%s WHERE room_id=%s",
        (data['hostel_name'], data['room_number'], data['capacity'], data['current_occupants'], room_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room updated successfully'})

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Rooms WHERE room_id=%s", (room_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room deleted successfully'})

# -------- Allocations CRUD --------
@app.route('/allocations', methods=['GET'])
@login_required
def get_allocations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.allocations_id, s.name, s.matric_number, r.room_number, a.date_allocated
        FROM Allocations a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Rooms r ON a.room_id = r.room_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    allocations = [
        {
            'allocations_id': r[0], 'student_name': r[1], 'matric_number': r[2],
            'room_number': r[3], 'date_allocated': r[4].strftime('%Y-%m-%d')
        } for r in rows
    ]
    return jsonify(allocations)

@app.route('/allocations', methods=['POST'])
@login_required
def add_allocation():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Allocations (student_id, room_id, date_allocated) VALUES (%s, %s, %s)",
        (data['student_id'], data['room_id'], data['date_allocated'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Allocation added successfully'})

@app.route('/allocations/<int:allocation_id>', methods=['PUT'])
@login_required
def update_allocation(allocation_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Allocations SET student_id=%s, room_id=%s, date_allocated=%s WHERE allocations_id=%s",
        (data['student_id'], data['room_id'], data['date_allocated'], allocation_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Allocation updated successfully'})

@app.route('/allocations/<int:allocation_id>', methods=['DELETE'])
@login_required
def delete_allocation(allocation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Allocations WHERE allocations_id=%s", (allocation_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Allocation deleted successfully'})

# -------- Payments CRUD --------
@app.route('/payments', methods=['GET'])
@login_required
def get_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payment_id, student_id, payment_method, purpose, status FROM Payments")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    payments = [
        {
            'payment_id': r[0], 'student_id': r[1], 'payment_method': r[2],
            'purpose': r[3], 'status': r[4]
        } for r in rows
    ]
    return jsonify(payments)

@app.route('/payments', methods=['POST'])
@login_required
def add_payment():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Payments (student_id, payment_method, purpose, status) VALUES (%s, %s, %s, %s)",
        (data['student_id'], data['payment_method'], data['purpose'], data['status'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Payment added successfully'})

@app.route('/payments/<int:payment_id>', methods=['PUT'])
@login_required
def update_payment(payment_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Payments SET student_id=%s, payment_method=%s, purpose=%s, status=%s WHERE payment_id=%s",
        (data['student_id'], data['payment_method'], data['purpose'], data['status'], payment_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Payment updated successfully'})

@app.route('/payments/<int:payment_id>', methods=['DELETE'])
@login_required
def delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Payments WHERE payment_id=%s", (payment_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Payment deleted successfully'})

# -------- Maintenance CRUD --------
@app.route('/maintenance', methods=['GET'])
@login_required
def get_maintenance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Maintenance")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    maintenance = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    return jsonify(maintenance)

@app.route('/maintenance', methods=['POST'])
@login_required
def add_maintenance():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Maintenance (room_id, issue_description, status, reported_date) VALUES (%s, %s, %s, %s)",
        (data['room_id'], data['issue_description'], data['status'], data['reported_date'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Maintenance issue reported successfully'})

@app.route('/maintenance/<int:maintenance_id>', methods=['PUT'])
@login_required
def update_maintenance(maintenance_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Maintenance SET room_id=%s, issue_description=%s, status=%s, reported_date=%s WHERE maintenance_id=%s",
        (data['room_id'], data['issue_description'], data['status'], data['reported_date'], maintenance_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Maintenance issue updated successfully'})

@app.route('/maintenance/<int:maintenance_id>', methods=['DELETE'])
@login_required
def delete_maintenance(maintenance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Maintenance WHERE maintenance_id=%s", (maintenance_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Maintenance issue deleted successfully'})



# ----------------------------------------
# API ROUTES: STUDENTS
# ----------------------------------------

# ---------- STUDENTS ----------
@app.route("/api/students", methods=["GET"])
@login_required
def api_get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            "student_id": r[0],
            "name": r[1],
            "matric_number": r[2],
            "department": r[3],
            "level": r[4],
            "gender": r[5]
        }
        for r in rows
    ])

# Create a student
@app.route("/api/students", methods=["POST"])
@login_required
def api_create_student():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Students (name, matric_number, department, level, gender)
        VALUES (%s, %s, %s, %s, %s)
    """, (data["name"], data["matric_number"], data["department"], data["level"], data["gender"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student created successfully"}), 201

# Update a student
@app.route("/api/students/<int:student_id>", methods=["PUT"])
@login_required
def api_update_student(student_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Students
        SET name=%s, matric_number=%s, department=%s, level=%s, gender=%s
        WHERE student_id=%s
    """, (data["name"], data["matric_number"], data["department"], data["level"], data["gender"], student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student updated successfully"})

# Delete a student
# Delete a student
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
@login_required
def api_delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Check for Allocations
        cursor.execute("SELECT COUNT(*) FROM Allocations WHERE student_id = %s", (student_id,))
        allocation_count = cursor.fetchone()[0]

        # Step 2: Check for Payments
        cursor.execute("SELECT COUNT(*) FROM Payments WHERE student_id = %s", (student_id,))
        payment_count = cursor.fetchone()[0]

        if allocation_count > 0 or payment_count > 0:
            related_tables = []
            if allocation_count > 0:
                related_tables.append("allocations")
            if payment_count > 0:
                related_tables.append("payments")

            return jsonify({
                "error": f"Cannot delete student — they still have records in {', '.join(related_tables)}. "
                         "Please remove those records first."
            }), 400

        # Step 3: Safe to delete
        cursor.execute("DELETE FROM Students WHERE student_id = %s", (student_id,))
        conn.commit()

        return jsonify({"message": "Student deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

# ----------------------------------------
# Export students to PDF

@app.route('/api/students/export-pdf', methods=['GET'])
@login_required
def export_students_pdf():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, matric_number, department, level, gender FROM Students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, height - 50, "Student List")

    # Table headers
    pdf.setFont("Helvetica-Bold", 12)
    headers = ["ID", "Name", "Matric No", "Department", "Level", "Gender"]
    y = height - 80
    x_positions = [50, 90, 200, 300, 420, 480]
    for i, header in enumerate(headers):
        pdf.drawString(x_positions[i], y, header)

    # Table rows
    pdf.setFont("Helvetica", 11)
    y -= 20
    for student in students:
        if y < 50:  # Start new page if near bottom
            pdf.showPage()
            y = height - 50
        for i, value in enumerate(student):
            pdf.drawString(x_positions[i], y, str(value))
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="students.pdf", mimetype='application/pdf')



# ----------------------------------------
# API ROUTES: ROOMS
# ----------------------------------------

@app.route("/api/rooms", methods=["GET"])
@login_required
def api_get_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Rooms")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            "room_id": r[0],
            "hostel_name": r[1],
            "room_number": r[2],
            "capacity": r[3],
            "current_occupants": r[4]
        }
        for r in rows
    ])

# Create room
@app.route("/api/rooms", methods=["POST"])
@login_required
def api_create_room():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Rooms (hostel_name, room_number, capacity, current_occupants)
        VALUES (%s, %s, %s, %s)
    """, (data["hostel_name"], data["room_number"], data["capacity"], data["current_occupants"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Room created successfully"}), 201

# Update room
@app.route("/api/rooms/<int:room_id>", methods=["PUT"])
@login_required
def api_update_room(room_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Rooms
        SET hostel_name=%s, room_number=%s, capacity=%s, current_occupants=%s
        WHERE room_id=%s
    """, (data["hostel_name"], data["room_number"], data["capacity"], data["current_occupants"], room_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Room updated successfully"})

# Delete room
@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
@login_required
def api_delete_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for allocations first
    cursor.execute("SELECT COUNT(*) FROM Allocations WHERE room_id = %s", (room_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "Room cannot be deleted. It is currently allocated."}), 400

    # Safe to delete
    cursor.execute("DELETE FROM Rooms WHERE room_id = %s", (room_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Room deleted successfully"})


@app.route("/api/rooms/available", methods=["GET"])
@login_required
def api_check_available_rooms():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM Rooms WHERE current_occupants < capacity
    """)
    available_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    if available_count == 0:
        return jsonify({"available": False})
    return jsonify({"available": True})


# ----------------------------------------
# API ROUTES: ALLOCATIONS
# ----------------------------------------
@app.route("/api/allocations", methods=["GET"])
@login_required
def api_get_allocations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
       SELECT A.allocations_id, S.name, S.matric_number, R.room_number, R.hostel_name, A.date_allocated
       FROM Allocations A
       JOIN Students S ON A.student_id = S.student_id
       JOIN Rooms R ON A.room_id = R.room_id
""") 
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        { "allocations_id": r[0],
          "name": r[1],
          "matric": r[2],
          "room_number": r[3],
          "hostel_name": r[4],
          "allocated_date": r[5].strftime("%Y-%m-%d") if r[5] else None
        }
        for r in rows
    ])
# Create allocation with transaction + rollback + payment check
@app.route("/api/allocations", methods=["POST"])
@login_required
def api_create_allocation():
    data = request.json
    student_id = data["student_id"]
    room_id = data["room_id"]
    date_allocated = data["date_allocated"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 🔒 Require at least one successful payment before allocation
        # If you want to require a specific purpose (e.g., Hostel Fee), add AND purpose = 'Hostel Fee'
        cursor.execute("""
            SELECT 1
            FROM Payments
            WHERE student_id = %s AND status = 'Paid'
            LIMIT 1
        """, (student_id,))
        has_paid = cursor.fetchone()
        if not has_paid:
            return jsonify({"error": "Payment required before allocation"}), 403

        # ✅ Check if student is already allocated
        cursor.execute("SELECT 1 FROM Allocations WHERE student_id = %s LIMIT 1", (student_id,))
        if cursor.fetchone():
            return jsonify({"error": "Student already has an allocation"}), 400

        # ✅ Check room exists & capacity
        cursor.execute("SELECT capacity, current_occupants FROM Rooms WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        if not room:
            return jsonify({"error": "Room not found"}), 404

        capacity, current_occupants = room
        if current_occupants >= capacity:
            return jsonify({"error": "Room is already full"}), 400

        # 🔁 Transaction: insert allocation + bump occupants
        cursor.execute("""
            INSERT INTO Allocations (student_id, room_id, date_allocated)
            VALUES (%s, %s, %s)
        """, (student_id, room_id, date_allocated))
        cursor.execute("""
            UPDATE Rooms SET current_occupants = current_occupants + 1
            WHERE room_id = %s
        """, (room_id,))
        conn.commit()
        return jsonify({"message": "Allocation created successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to create allocation: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()



# Update allocation
@app.route("/api/allocations/<int:allocations_id>", methods=["PUT"])
@login_required
def api_update_allocation(allocations_id):
    data = request.json
    new_student_id = data["student_id"]
    new_room_id = data["room_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get current allocation details
    cursor.execute("SELECT room_id, student_id FROM Allocations WHERE allocations_id=%s", (allocations_id,))
    current_allocation = cursor.fetchone()
    if not current_allocation:
        cursor.close()
        conn.close()
        return jsonify({"error": "Allocation not found"}), 404

    old_room_id, old_student_id = current_allocation

    # 2. If moving to a new room, check capacity
    if old_room_id != new_room_id:
        cursor.execute("SELECT capacity, current_occupants FROM Rooms WHERE room_id=%s", (new_room_id,))
        room = cursor.fetchone()
        if not room:
            cursor.close()
            conn.close()
            return jsonify({"error": "New room not found"}), 404

        capacity, current_occupants = room
        if current_occupants >= capacity:
            cursor.close()
            conn.close()
            return jsonify({"error": "New room is already full"}), 400

    # 3. Update the allocation record
    cursor.execute("""
        UPDATE Allocations
        SET student_id=%s, room_id=%s
        WHERE allocations_id=%s
    """, (new_student_id, new_room_id, allocations_id))

    # 4. Update occupants if the room changed
    if old_room_id != new_room_id:
        cursor.execute("UPDATE Rooms SET current_occupants = current_occupants - 1 WHERE room_id=%s", (old_room_id,))
        cursor.execute("UPDATE Rooms SET current_occupants = current_occupants + 1 WHERE room_id=%s", (new_room_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Allocation updated successfully"})


# Delete allocation
@app.route("/api/allocations/<int:allocations_id>", methods=["DELETE"])
@login_required
def api_delete_allocation(allocations_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Find allocation before deleting
    cursor.execute("SELECT room_id FROM Allocations WHERE allocations_id= %s", (allocations_id,))
    allocation = cursor.fetchone()
    if not allocation:
        cursor.close()
        conn.close()
        return jsonify({"error": "Allocation not found"}), 404

    room_id = allocation[0]

    # 2. Delete the allocation
    cursor.execute("DELETE FROM Allocations WHERE allocations_id=%s", (allocations_id,))

    # 3. Reduce occupants count for that room
    cursor.execute("UPDATE Rooms SET current_occupants = current_occupants - 1 WHERE room_id=%s", (room_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Allocation deleted successfully"})




# ----------------------------------------
# API ROUTES: PAYMENTS
# ----------------------------------------
@app.route("/api/payments", methods=["GET"])
@login_required
def api_get_payments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            P.payment_id, 
            S.student_id,
            S.name, 
            S.matric_number, 
            P.amount,
            P.payment_date,
            P.payment_method, 
            P.purpose, 
            P.status,
            P.receipt_no
        FROM Payments P
        JOIN Students S ON P.student_id = S.student_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            "payment_id": r[0],
            "student_id": r[1],
            "student_name": r[2],
            "matric": r[3],
            "amount": r[4],
            "payment_date": r[5],
            "method": r[6],
            "purpose": r[7],
            "status": r[8],
            "receipt_no": r[9]
        }
        for r in rows
    ])


# Create payment (auto-generate receipt, validate, rollback on error)
@app.route("/api/payments", methods=["POST"])
@login_required
def api_add_payment():
    data = request.json
    student_id = data.get("student_id")
    payment_method = data.get("payment_method")
    amount = data.get("amount")
    purpose = data.get("purpose")
    status = data.get("status")             # "Paid" / "Pending"
    payment_date = data.get("payment_date") # optional: 'YYYY-MM-DD'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Basic validation
        if not student_id or not amount or not payment_method or not purpose or not status:
            return jsonify({"error": "Missing required fields"}), 400

        # Ensure student exists
        cursor.execute("SELECT 1 FROM Students WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # Normalize amount
        try:
            amount = float(amount)
        except:
            return jsonify({"error": "Amount must be numeric"}), 400

        # Generate a unique receipt number
        receipt_no = _get_unique_receipt_no(cursor)

        # Insert
        if payment_date:
            cursor.execute("""
                INSERT INTO Payments (student_id, payment_method, amount, purpose, status, receipt_no, payment_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_id, payment_method, amount, purpose, status, receipt_no, payment_date))
        else:
            cursor.execute("""
                INSERT INTO Payments (student_id, payment_method, amount, purpose, status, receipt_no)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, payment_method, amount, purpose, status, receipt_no))

        conn.commit()
        return jsonify({"message": "Payment added successfully", "receipt_no": receipt_no}), 201

    except Exception as e:
        conn.rollback()
        print("Error inserting payment:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Update payment
@app.route("/api/payments/<int:payment_id>", methods=["PUT"])
@login_required
def api_update_payment(payment_id):
    data = request.json
    student_id = data.get("student_id")
    payment_method = data.get("payment_method")
    amount = data.get("amount")
    purpose = data.get("purpose")
    status = data.get("status")
    receipt_no = data.get("receipt_no")
    payment_date = data.get("payment_date")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure payment exists
        cursor.execute("SELECT 1 FROM Payments WHERE payment_id = %s", (payment_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Payment not found"}), 404

        # Validate student exists
        cursor.execute("SELECT 1 FROM Students WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # Unique receipt check (exclude current record)
        if receipt_no:
            cursor.execute("""
                SELECT 1 FROM Payments WHERE receipt_no = %s AND payment_id <> %s
            """, (receipt_no, payment_id))
            if cursor.fetchone():
                return jsonify({"error": "Duplicate receipt number"}), 400

        # Update (with or without payment_date)
        if payment_date:
            cursor.execute("""
                UPDATE Payments
                SET student_id = %s, payment_method = %s, amount = %s, purpose = %s, status = %s, receipt_no = %s, payment_date = %
s
                WHERE payment_id = %s
            """, (student_id, payment_method, amount, purpose, status, receipt_no, payment_date, payment_id))
        else:
            cursor.execute("""
                UPDATE Payments
                SET student_id = %s, payment_method = %s, amount = %s, purpose = %s, status = %s, receipt_no = %s
                WHERE payment_id = %s
            """, (student_id, payment_method, amount, purpose, status, receipt_no, payment_id))

        conn.commit()
        return jsonify({"message": "Payment updated successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/payments/<int:payment_id>", methods=["DELETE"])
@login_required
def api_delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Payments WHERE payment_id = %s", (payment_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Payment not found"}), 404
        conn.commit()
        return jsonify({"message": "Payment deleted successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ----------------------------------------
# API ROUTES: MAINTENANCE
# ----------------------------------------

# GET: Fetch all maintenance records
@app.route("/api/maintenance", methods=["GET"])
@login_required
def api_get_maintenance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Maintenance")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([
        {
            "maintenance_id": r[0],
            "room_id": r[1],
            "issue": r[2],
            "reported_on": r[3],
            "status": r[4]
        }
        for r in rows
    ])


# POST: Add a new maintenance record
@app.route("/api/maintenance", methods=["POST"])
@login_required
def api_add_maintenance():
    try:
        data = request.get_json()
         # Ensure required fields are present
        room_id = int(data.get("room_id", 0 ))
        issue_description = data.get("issue_description", "").strip() # JS calls it 'issue'
        date_reported = data.get("date_reported", "").strip()
        status = data.get("status", "").strip()
        if not room_id or not issue_description or not date_reported and status:
            return jsonify({"error": "Missing required fields"}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Maintenance (room_id, issue_description, date_reported, status)
            VALUES (%s, %s, %s, %s)
        """, (room_id, issue_description, date_reported, status))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Maintenance record added successfully"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print the full traceback for debugging
        print("Error in POST /api/maintenance:", e)
        return jsonify({"error": str(e)}), 500



# PUT: Update an existing maintenance record
@app.route("/api/maintenance/<int:issue_id>", methods=["PUT"])
@login_required
def api_update_maintenance(issue_id):
    data = request.json
    print("DATA RECEIVED:", data)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Maintenance
            SET room_id = %s, issue_description = %s, date_reported = %s, status = %s
            WHERE issue_id = %s
        """, (
            data["room_id"],
            data["issue_description"],
            data['date_reported'],
            data["status"],
            issue_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Maintenance record updated successfully"})
    except Exception as e:
        print("Error in PUT /api/maintenance:", str(e))
        return jsonify({"error": "Failed to update maintenance record"}), 500




# DELETE: Delete a maintenance record
@app.route("/api/maintenance/<int:issue_id>", methods=["DELETE"])
@login_required
def api_delete_maintenance(issue_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Maintenance WHERE issue_id = %s", (issue_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Maintenance deleted successfully"})

    except Exception as e:
        print("Error in DELETE /api/maintenance:", e)
        return jsonify({"error": str(e)}), 500


    
    

# ==========================
#         ENTRY POINT
# ==========================
if __name__ == '__main__':
    # Use the port Render provides, or default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


