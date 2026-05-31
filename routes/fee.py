from flask import Blueprint, request, jsonify
import database
import algorithms

fee_bp = Blueprint('fee', __name__)

@fee_bp.route('/api/fees/calculate', methods=['POST'])
def calculate_fee_api():
    try:
        data = request.json or {}
        tuition = data.get('tuition_fee', 0)
        hostel = data.get('hostel_fee', 0)
        transport = data.get('transport_fee', 0)
        
        total = algorithms.calculate_total_fee(tuition, hostel, transport)
        return jsonify({"tuition_fee": tuition, "hostel_fee": hostel, "transport_fee": transport, "total_fee": total})
    except Exception as e:
        return jsonify({"error": f"Fee calculation failed: {str(e)}"}), 400

@fee_bp.route('/api/fees/update', methods=['POST'])
def update_student_fees():
    try:
        data = request.json or {}
        student_id = data.get('student_id', '').strip()
        
        if not student_id:
            return jsonify({"error": "Student ID is required."}), 400
            
        try:
            tuition_fee = float(data.get('tuition_fee', 0) or 0)
            hostel_fee = float(data.get('hostel_fee', 0) or 0)
            transport_fee = float(data.get('transport_fee', 0) or 0)
            
            if tuition_fee < 0 or hostel_fee < 0 or transport_fee < 0:
                return jsonify({"error": "Fees cannot be negative numbers."}), 400
        except ValueError:
            return jsonify({"error": "Fee inputs must be valid numbers."}), 400
            
        # Reusable fee calculation function
        total_fee = algorithms.calculate_total_fee(tuition_fee, hostel_fee, transport_fee)
        
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check student exists
        cursor.execute("SELECT name FROM students WHERE student_id = ?;", (student_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Student with ID '{student_id}' does not exist."}), 404
            
        # Update
        cursor.execute("""
            UPDATE students 
            SET tuition_fee = ?, hostel_fee = ?, transport_fee = ?, total_fee = ?
            WHERE student_id = ?;
        """, (tuition_fee, hostel_fee, transport_fee, total_fee, student_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"Fees updated successfully for Student {student_id}.",
            "total_fee": total_fee
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update fees: {str(e)}"}), 500
