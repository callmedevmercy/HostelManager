import os
import psycopg2
from dotenv import load_dotenv

# Load your Render External Database URL from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Your translated PostgreSQL schema
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS Students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    matric_number VARCHAR(15) UNIQUE,
    department VARCHAR(50),
    level VARCHAR(20),
    gender VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Rooms (
    room_id SERIAL PRIMARY KEY,
    hostel_name VARCHAR(100),
    room_number VARCHAR(50) UNIQUE,
    capacity INT,
    current_occupants INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Allocations(
    allocations_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES Students(student_id),
    room_id INT REFERENCES Rooms(room_id),
    date_allocated DATE
);

CREATE TABLE IF NOT EXISTS Maintenance (
    issue_id SERIAL PRIMARY KEY,
    room_id INT REFERENCES Rooms(room_id),
    issue_description TEXT,
    date_reported DATE,
    status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Admins(
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Payments (
    payment_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES Students(student_id),
    amount DECIMAL(10, 2),
    payment_date DATE,
    payment_method VARCHAR(30),
    purpose VARCHAR(50),
    status VARCHAR(20),
    receipt_no VARCHAR(20) UNIQUE NOT NULL
);

-- Add a default admin so you don't get locked out of your own system!
INSERT INTO Admins (username, password) VALUES ('admin', 'admin123') ON CONFLICT DO NOTHING;
"""

def build_database():
    try:
        print("Connecting to Render database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Creating tables...")
        cursor.execute(CREATE_TABLES_SQL)
        conn.commit()
        
        print("✅ Success! All HostelManager tables are live on the cloud.")
        
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == '__main__':
    build_database()