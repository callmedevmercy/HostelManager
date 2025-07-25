# ==========================================
# HostelTrackerERP Flask App
# ------------------------------------------
# Author: You
# Description: This app handles authentication and CRUD operations
#              for students, rooms, allocations, payments, and maintenance.
# ==========================================

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Secret key for sessions (should be set in .env for production)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# ============================
#   DATABASE CONNECTION SETUP
# ============================
def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')}"
    )

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
            "SELECT username, password FROM Admins WHERE username = ? AND password = ?", 
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
        "INSERT INTO Students (name, matric_number, department, level, gender) VALUES (?, ?, ?, ?, ?)",
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
        "UPDATE Students SET name=?, matric_number=?, department=?, level=?, gender=? WHERE student_id=?",
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
    cursor.execute("DELETE FROM Students WHERE student_id=?", (student_id))
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
        "INSERT INTO Rooms (hostel_name, room_number, capacity, current_occupants) VALUES (?, ?, ?, ?)",
        data['hostel_name'], data['room_number'], data['capacity'], data['current_occupants']
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
        "UPDATE Rooms SET hostel_name=?, room_number=?, capacity=?, current_occupants=? WHERE room_id=?",
        data['hostel_name'], data['room_number'], data['capacity'], data['current_occupants'], room_id
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Room updated successfully'})

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Rooms WHERE room_id=?", room_id)
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
        "INSERT INTO Allocations (student_id, room_id, date_allocated) VALUES (?, ?, ?)",
        data['student_id'], data['room_id'], data['date_allocated']
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
        "UPDATE Allocations SET student_id=?, room_id=?, date_allocated=? WHERE allocations_id=?",
        data['student_id'], data['room_id'], data['date_allocated'], allocation_id
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Allocation updated successfully'})

@app.route('/allocations/<int:allocation_id>', methods=['DELETE'])
@login_required
def delete_allocation(allocation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Allocations WHERE allocations_id=?", allocation_id)
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
        "INSERT INTO Payments (student_id, payment_method, purpose, status) VALUES (?, ?, ?, ?)",
        data['student_id'], data['payment_method'], data['purpose'], data['status']
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
        "UPDATE Payments SET student_id=?, payment_method=?, purpose=?, status=? WHERE payment_id=?",
        data['student_id'], data['payment_method'], data['purpose'], data['status'], payment_id
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Payment updated successfully'})

@app.route('/payments/<int:payment_id>', methods=['DELETE'])
@login_required
def delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Payments WHERE payment_id=?", payment_id)
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
        "INSERT INTO Maintenance (room_id, issue_description, status, reported_date) VALUES (?, ?, ?, ?)",
        data['room_id'], data['issue_description'], data['status'], data['reported_date']
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
        "UPDATE Maintenance SET room_id=?, issue_description=?, status=?, reported_date=? WHERE maintenance_id=?",
        data['room_id'], data['issue_description'], data['status'], data['reported_date'], maintenance_id
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Maintenance issue updated successfully'})

@app.route('/maintenance/<int:maintenance_id>', methods=['DELETE'])
@login_required
def delete_maintenance(maintenance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Maintenance WHERE maintenance_id=?", maintenance_id)
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
        VALUES (?, ?, ?, ?, ?)
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
        SET name=?, matric_number=?, department=?, level=?, gender=?
        WHERE student_id=?
    """, (data["name"], data["matric_number"], data["department"], data["level"], data["gender"], student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student updated successfully"})

# Delete a student
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
@login_required
def api_delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE student_id=?", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student deleted successfully"})


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
        VALUES (?, ?, ?, ?)
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
        SET hostel_name=?, room_number=?, capacity=?, current_occupants=?
        WHERE room_id=?
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
    cursor.execute("DELETE FROM Rooms WHERE room_id=?", (room_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Room deleted successfully"})


# ----------------------------------------
# API ROUTES: ALLOCATIONS
# ----------------------------------------
@app.route("/api/allocations", methods=["GET"])
@login_required
def api_get_allocations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT A.allocations_id, S.name, S.matric_number, R.room_number
        FROM Allocations A
        JOIN Students S ON A.student_id = S.student_id
        JOIN Rooms R ON A.room_id = R.room_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            "allocations_id": r[0],
            "name": r[1],
            "matric": r[2],
            "room_number": r[3]
        }
        for r in rows
    ])

# Create allocation
@app.route("/api/allocations", methods=["POST"])
@login_required
def api_create_allocation():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Allocations (student_id, room_id)
        VALUES (?, ?)
    """, (data["student_id"], data["room_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Allocation created successfully"}), 201

# Update allocation
@app.route("/api/allocations/<int:allocations_id>", methods=["PUT"])
@login_required
def api_update_allocation(allocations_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Allocations
        SET student_id=?, room_id=?
        WHERE allocations_id=?
    """, (data["student_id"], data["room_id"], allocations_id))
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
    cursor.execute("DELETE FROM Allocations WHERE allocations_id=?", (allocations_id,))
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
            S.name, 
            S.matric_number, 
            P.amount,
            P.payment_date,
            P.payment_method, 
            P.purpose, 
            P.status
        FROM Payments P
        JOIN Students S ON P.student_id = S.student_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {
            "payment_id": r[0],
            "student_name": r[1],
            "matric": r[2],
            "amount": r[3],
            "payment_date": r[4],
            "method": r[5],
            "purpose": r[6],
            "status": r[7]
        }
        for r in rows
    ])


# Create payment
@app.route("/api/payments", methods=["POST"])
@login_required
def api_create_payment():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Payments (student_id, payment_method, purpose, status)
        VALUES (?, ?, ?, ?)
    """, (data["student_id"], data["payment_method"], data["purpose"], data["status"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Payment created successfully"}), 201

# Update payment
@app.route("/api/payments/<int:payment_id>", methods=["PUT"])
@login_required
def api_update_payment(payment_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Payments
        SET student_id=?, payment_method=?, purpose=?, status=?
        WHERE payment_id=?
    """, (data["student_id"], data["payment_method"], data["purpose"], data["status"], payment_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Payment updated successfully"})

# Delete payment
@app.route("/api/payments/<int:payment_id>", methods=["DELETE"])
@login_required
def api_delete_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Payments WHERE payment_id=?", (payment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Payment deleted successfully"})

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

        room_id = data.get("room_id")
        issue = data.get("issue")
        status = data.get("status")
        reported_on = data.get("reported_on")  # Should be ISO format like "2025-07-18T14:30:00"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Maintenance (room_id, issue, status, reported_on)
            VALUES (?, ?, ?, ?)
        """, (room_id, issue, status, reported_on))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Maintenance record added successfully"}), 201

    except Exception as e:
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
            SET room_id = ?, issue_description = ?, date_reported = ?, status = ?
            WHERE issue_id = ?
        """, (
            data["room_id"],
            data["issue_description"],
            data["date_reported"],
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
@app.route("/api/maintenance/<int:maintenance_id>", methods=["DELETE"])
@login_required
def api_delete_maintenance(maintenance_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Maintenance WHERE maintenance_id = ?", (maintenance_id,))
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
    app.run(debug=True, host='0.0.0.0')


