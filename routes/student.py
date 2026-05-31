from flask import Blueprint, request, jsonify
import database
import algorithms

student_bp = Blueprint('student', __name__)

@student_bp.route('/api/students', methods=['GET'])
def get_students():
    try:
        sort_by = request.args.get('sort_by', 'student_id')
        reverse = request.args.get('reverse', 'false').lower() == 'true'
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Select students
        cursor.execute("SELECT * FROM students;")
        rows = cursor.fetchall()
        
        # Convert sqlite Row objects to a list of dicts
        students = []
        for r in rows:
            s_dict = dict(r)
            
            # Fetch enrolled courses for this student
            cursor.execute("""
                SELECT c.course_code, c.course_name, c.credits 
                FROM student_courses sc
                JOIN courses c ON sc.course_code = c.course_code
                WHERE sc.student_id = ?;
            """, (s_dict['student_id'],))
            s_dict['courses'] = [dict(c_row) for c_row in cursor.fetchall()]
            
            students.append(s_dict)
            
        conn.close()
        
        # Use our custom Bubble Sort implementation
        sorted_students = algorithms.bubble_sort(students, key=sort_by, reverse=reverse)
        
        return jsonify(sorted_students)
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve students: {str(e)}"}), 500

@student_bp.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.json or {}
        student_id = data.get('student_id', '').strip()
        name = data.get('name', '').strip()
        
        if not student_id or not name:
            return jsonify({"error": "Student ID and Name are required."}), 400
            
        try:
            age = int(data.get('age', 0))
            if age <= 0:
                raise ValueError()
        except ValueError:
            return jsonify({"error": "Age must be a positive integer."}), 400
            
        try:
            score = float(data.get('score', 0))
            if not (0 <= score <= 100):
                return jsonify({"error": "Score must be between 0 and 100."}), 400
        except ValueError:
            return jsonify({"error": "Score must be a number."}), 400
            
        # Fee values
        tuition_fee = float(data.get('tuition_fee', 0) or 0)
        hostel_fee = float(data.get('hostel_fee', 0) or 0)
        transport_fee = float(data.get('transport_fee', 0) or 0)
        
        # Evaluate Grade
        grade, remark = algorithms.evaluate_grade(score)
        
        # Calculate Total Fee
        total_fee = algorithms.calculate_total_fee(tuition_fee, hostel_fee, transport_fee)
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check if ID exists
        cursor.execute("SELECT id FROM students WHERE student_id = ?;", (student_id,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Student with ID '{student_id}' already exists."}), 400
            
        # Insert
        cursor.execute("""
            INSERT INTO students (
                student_id, name, age, score, grade, remark, tuition_fee, hostel_fee, transport_fee, total_fee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (student_id, name, age, score, grade, remark, tuition_fee, hostel_fee, transport_fee, total_fee))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"Student {name} registered successfully."})
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@student_bp.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM students WHERE student_id = ?;", (student_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": f"Student with ID '{student_id}' not found."}), 404
            
        name = row['name']
        
        # Delete student (foreign key cascade deletes enrollments)
        cursor.execute("DELETE FROM students WHERE student_id = ?;", (student_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": f"Student {name} ({student_id}) deleted successfully."})
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete student: {str(e)}"}), 500

@student_bp.route('/api/students/search', methods=['GET'])
def search_student():
    try:
        target_id = request.args.get('student_id', '').strip()
        method = request.args.get('method', 'linear').lower()
        
        if not target_id:
            return jsonify({"error": "Search Target Student ID is required."}), 400
            
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students;")
        rows = cursor.fetchall()
        
        students = [dict(r) for r in rows]
        conn.close()
        
        if method == 'binary':
            found, steps = algorithms.binary_search(students, target_id)
        else:
            found, steps = algorithms.linear_search(students, target_id)
            
        return jsonify({
            "found": found,
            "steps": steps,
            "method": method
        })
        
    except Exception as e:
        return jsonify({"error": f"Search execution failed: {str(e)}"}), 500
