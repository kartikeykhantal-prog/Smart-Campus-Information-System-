from flask import Flask, render_template, jsonify, send_file, request
import os
import io
import json
import sqlite3
import database
from routes import student_bp, course_bp, fee_bp, scanner_bp, analytics_bp

app = Flask(__name__)

# Configure Secret Key for Flask sessions if needed
app.secret_key = 'antigravity_campus_secret_key'

# Register modular blueprints
app.register_blueprint(student_bp)
app.register_blueprint(course_bp)
app.register_blueprint(fee_bp)
app.register_blueprint(scanner_bp)
app.register_blueprint(analytics_bp)

@app.route('/')
def index():
    return render_template('index.html')

# File Backup Management System API Endpoints (Core Module 6)
@app.route('/api/file/export', methods=['GET'])
def export_database():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Read students
        cursor.execute("SELECT * FROM students;")
        students = [dict(r) for r in cursor.fetchall()]
        
        # Read courses
        cursor.execute("SELECT * FROM courses;")
        courses = [dict(r) for r in cursor.fetchall()]
        
        # Read enrollments
        cursor.execute("SELECT * FROM student_courses;")
        enrollments = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        
        backup_data = {
            "version": "1.0",
            "students": students,
            "courses": courses,
            "enrollments": enrollments
        }
        
        # Create an in-memory JSON file stream
        json_str = json.dumps(backup_data, indent=2)
        stream = io.BytesIO(json_str.encode('utf-8'))
        
        return send_file(
            stream,
            mimetype='application/json',
            as_attachment=True,
            download_name='student_campus_backup.json'
        )
        
    except Exception as e:
        return jsonify({"error": f"Database backup compilation failed: {str(e)}"}), 500

@app.route('/api/file/import', methods=['POST'])
def import_database():
    try:
        data = request.json or {}
        
        students = data.get('students', [])
        courses = data.get('courses', [])
        enrollments = data.get('enrollments', [])
        
        # Open DB connection
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Enable Foreign Key validations
        cursor.execute("PRAGMA foreign_keys = OFF;") # Temporarily disable to clear tables
        
        # Clear tables
        cursor.execute("DELETE FROM student_courses;")
        cursor.execute("DELETE FROM students;")
        cursor.execute("DELETE FROM courses;")
        
        # Re-enable Foreign Key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Import Courses
        for c in courses:
            cursor.execute("""
                INSERT OR IGNORE INTO courses (course_code, course_name, credits) 
                VALUES (?, ?, ?);
            """, (c.get('course_code'), c.get('course_name'), c.get('credits')))
            
        # Import Students
        for s in students:
            cursor.execute("""
                INSERT OR IGNORE INTO students (
                    student_id, name, age, score, grade, remark, tuition_fee, hostel_fee, transport_fee, total_fee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                s.get('student_id'), s.get('name'), s.get('age'), s.get('score'), 
                s.get('grade'), s.get('remark'), s.get('tuition_fee'), 
                s.get('hostel_fee'), s.get('transport_fee'), s.get('total_fee')
            ))
            
        # Import Enrollments
        for e in enrollments:
            cursor.execute("""
                INSERT OR IGNORE INTO student_courses (student_id, course_code) 
                VALUES (?, ?);
            """, (e.get('student_id'), e.get('course_code')))
            
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Database backup restored successfully."})
        
    except Exception as e:
        return jsonify({"error": f"Restore failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Initialize the database on startup
    database.init_db()
    
    # Run the development server
    # Listen on port 5000 (accessible on localhost)
    app.run(host='127.0.0.1', port=5000, debug=True)
