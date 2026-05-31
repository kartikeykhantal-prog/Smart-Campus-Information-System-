def evaluate_grade(score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return 'F', 'Invalid score'
    
    if score >= 90:
        return 'A', 'Excellent performance and outstanding understanding.'
    elif score >= 80:
        return 'B', 'Good performance and solid understanding.'
    elif score >= 70:
        return 'C', 'Satisfactory performance and fair understanding.'
    elif score >= 60:
        return 'D', 'Passing performance, needs improvement.'
    else:
        return 'F', 'Failed to meet minimum requirements. Please seek assistance.'

def calculate_total_fee(tuition, hostel, transport):
    try:
        t = float(tuition or 0)
        h = float(hostel or 0)
        tr = float(transport or 0)
        return t + h + tr
    except (ValueError, TypeError):
        return 0.0

def bubble_sort(students_list, key='student_id', reverse=False):
    # Bubble Sort implementation
    arr = list(students_list)
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            val1 = arr[j].get(key, '')
            val2 = arr[j+1].get(key, '')
            
            # Case-insensitive comparison if they are strings
            if isinstance(val1, str) and isinstance(val2, str):
                val1 = val1.lower()
                val2 = val2.lower()
            
            condition = val1 > val2 if not reverse else val1 < val2
            if condition:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def linear_search(students_list, target_id):
    steps = []
    found = None
    target_id_clean = str(target_id).strip().lower()
    
    for idx, student in enumerate(students_list):
        current_id = str(student.get('student_id', '')).strip()
        current_id_clean = current_id.lower()
        
        is_match = current_id_clean == target_id_clean
        step_info = {
            "index": idx,
            "student_id": current_id,
            "name": student.get('name', ''),
            "status": "Checking" if not is_match else "Found Match",
            "message": f"Step {idx + 1}: Checking index {idx} (Student ID: {current_id}). " + 
                       (f"Match found!" if is_match else f"No match.")
        }
        steps.append(step_info)
        
        if is_match:
            found = student
            break
            
    return found, steps

def binary_search(students_list, target_id):
    # Binary search requires the list to be sorted by student_id
    sorted_list = sorted(students_list, key=lambda x: str(x.get('student_id', '')).lower())
    steps = []
    found = None
    target_id_clean = str(target_id).strip().lower()
    
    low = 0
    high = len(sorted_list) - 1
    step_num = 1
    
    while low <= high:
        mid = (low + high) // 2
        current_student = sorted_list[mid]
        current_id = str(current_student.get('student_id', '')).strip()
        current_id_clean = current_id.lower()
        
        step_info = {
            "step": step_num,
            "low": low,
            "high": high,
            "mid": mid,
            "student_id": current_id,
            "name": current_student.get('name', ''),
            "message": f"Step {step_num}: range [{low}, {high}], checking midpoint index {mid} (Student ID: {current_id})."
        }
        
        if current_id_clean == target_id_clean:
            step_info["status"] = "Found Match"
            step_info["message"] += " Match found!"
            steps.append(step_info)
            found = current_student
            break
        elif current_id_clean < target_id_clean:
            step_info["status"] = "Too Low"
            step_info["message"] += " Target ID is higher. Searching right half."
            steps.append(step_info)
            low = mid + 1
        else:
            step_info["status"] = "Too High"
            step_info["message"] += " Target ID is lower. Searching left half."
            steps.append(step_info)
            high = mid - 1
            
        step_num += 1
        
    if not found and len(sorted_list) > 0:
        steps.append({
            "step": step_num,
            "low": low,
            "high": high,
            "mid": -1,
            "student_id": "",
            "status": "Not Found",
            "message": f"Search range empty. Target ID '{target_id}' not found."
        })
        
    return found, steps
