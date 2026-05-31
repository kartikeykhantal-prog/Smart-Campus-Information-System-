from flask import Blueprint, request, jsonify
import database

course_bp = Blueprint('course', __name__)

@course_bp.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses;")
        rows = cursor.fetchall()
        courses = [dict(r) for r in rows]
        conn.close()
        return jsonify(courses)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve courses: {str(e)}"}), 500

@course_bp.route('/api/courses', methods=['POST'])
def add_course():
    try:
        data = request.json or {}
        course_code = data.get('course_code', '').strip().upper()
        course_name = data.get('course_name', '').strip()
        
        if not course_code or not course_name:
            return jsonify({"error": "Course Code and Name are required."}), 400
            
        try:
            credits = int(data.get('credits', 0))
            if credits <= 0:
                return jsonify({"error": "Credits must be a positive integer."}), 400
        except ValueError:
            return jsonify({"error": "Credits must be an integer."}), 400
            
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check if course code exists
        cursor.execute("SELECT id FROM courses WHERE course_code = ?;", (course_code,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Course with code '{course_code}' already exists."}), 400
            
        cursor.execute("INSERT INTO courses (course_code, course_name, credits) VALUES (?, ?, ?);", 
                       (course_code, course_name, credits))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"Course {course_code} added successfully."})
        
    except Exception as e:
        return jsonify({"error": f"Failed to add course: {str(e)}"}), 500

@course_bp.route('/api/courses/<course_code>', methods=['DELETE'])
def delete_course(course_code):
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM courses WHERE course_code = ?;", (course_code,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Course {course_code} not found."}), 404
            
        cursor.execute("DELETE FROM courses WHERE course_code = ?;", (course_code,))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"Course {course_code} deleted successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to delete course: {str(e)}"}), 500

@course_bp.route('/api/enroll', methods=['POST'])
def enroll_student():
    try:
        data = request.json or {}
        student_id = data.get('student_id', '').strip()
        course_code = data.get('course_code', '').strip().upper()
        
        if not student_id or not course_code:
            return jsonify({"error": "Student ID and Course Code are required."}), 400
            
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check student exists
        cursor.execute("SELECT name FROM students WHERE student_id = ?;", (student_id,))
        student = cursor.fetchone()
        if not student:
            conn.close()
            return jsonify({"error": f"Student with ID '{student_id}' does not exist."}), 404
            
        # Check course exists
        cursor.execute("SELECT course_name, credits FROM courses WHERE course_code = ?;", (course_code,))
        course = cursor.fetchone()
        if not course:
            conn.close()
            return jsonify({"error": f"Course '{course_code}' does not exist."}), 404
            
        course_credits = course['credits']
        
        # Check current enrollments count
        cursor.execute("SELECT COUNT(*), SUM(c.credits) FROM student_courses sc JOIN courses c ON sc.course_code = c.course_code WHERE sc.student_id = ?;", (student_id,))
        count_row = cursor.fetchone()
        current_count = count_row[0] or 0
        current_credits = count_row[1] or 0
        
        # Check if already enrolled
        cursor.execute("SELECT id FROM student_courses WHERE student_id = ? AND course_code = ?;", (student_id, course_code))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Student is already enrolled in this course."}), 400
            
        # Validate limit: max 5 courses
        if current_count >= 5:
            conn.close()
            return jsonify({"error": "Enrollment limit exceeded: Students can enroll in a maximum of 5 courses."}), 400
            
        # Validate limit: max 18 credits
        if current_credits + course_credits > 18:
            conn.close()
            return jsonify({"error": f"Credit limit exceeded: Enrolling in this course would bring total credits to {current_credits + course_credits} (Max: 18 credits)."}), 400
            
        # Enroll
        cursor.execute("INSERT INTO student_courses (student_id, course_code) VALUES (?, ?);", (student_id, course_code))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"Successfully enrolled student in {course_code} ({course['course_name']})."})
        
    except Exception as e:
        return jsonify({"error": f"Enrollment operation failed: {str(e)}"}), 500

@course_bp.route('/api/unenroll', methods=['POST'])
def unenroll_student():
    try:
        data = request.json or {}
        student_id = data.get('student_id', '').strip()
        course_code = data.get('course_code', '').strip().upper()
        
        if not student_id or not course_code:
            return jsonify({"error": "Student ID and Course Code are required."}), 400
            
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM student_courses WHERE student_id = ? AND course_code = ?;", (student_id, course_code))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected == 0:
            return jsonify({"error": "Student was not enrolled in this course."}), 400
            
        return jsonify({"success": True, "message": f"Successfully unenrolled student from {course_code}."})
        
    except Exception as e:
        return jsonify({"error": f"Unenrollment failed: {str(e)}"}), 500
