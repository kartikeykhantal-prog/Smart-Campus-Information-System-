import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'campus.db')

def get_db_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        score REAL NOT NULL,
        grade TEXT NOT NULL,
        remark TEXT NOT NULL,
        tuition_fee REAL DEFAULT 0,
        hostel_fee REAL DEFAULT 0,
        transport_fee REAL DEFAULT 0,
        total_fee REAL DEFAULT 0
    );
    """)
    
    # Create courses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        course_name TEXT NOT NULL,
        credits INTEGER NOT NULL
    );
    """)
    
    # Create student course enrollment mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        course_code TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
        UNIQUE(student_id, course_code)
    );
    """)
    
    # Insert sample courses if table is empty
    cursor.execute("SELECT COUNT(*) FROM courses;")
    if cursor.fetchone()[0] == 0:
        sample_courses = [
            ("CS101", "Introduction to Computer Science", 4),
            ("MA101", "Calculus I", 4),
            ("PH101", "Engineering Physics", 3),
            ("EN101", "Technical Communication", 2),
            ("CS201", "Data Structures & Algorithms", 4)
        ]
        cursor.executemany("INSERT INTO courses (course_code, course_name, credits) VALUES (?, ?, ?);", sample_courses)
    
    # Insert sample students if empty
    cursor.execute("SELECT COUNT(*) FROM students;")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ("STU1001", "Alice Vance", 19, 95.0, "A", "Excellent", 8000.0, 1500.0, 500.0, 10000.0),
            ("STU1002", "Bob Smith", 20, 84.5, "B", "Good", 8000.0, 0.0, 500.0, 8500.0),
            ("STU1003", "Charlie Brown", 18, 72.0, "C", "Satisfactory", 8000.0, 1500.0, 0.0, 9500.0),
            ("STU1004", "Daisy Miller", 21, 58.0, "F", "Fail", 8000.0, 0.0, 0.0, 8000.0),
            ("STU1005", "Ethan Hunt", 22, 65.5, "D", "Pass", 8000.0, 1500.0, 500.0, 10000.0)
        ]
        cursor.executemany("""
            INSERT INTO students (
                student_id, name, age, score, grade, remark, tuition_fee, hostel_fee, transport_fee, total_fee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, sample_students)
        
        # Enroll sample students in some courses
        sample_enrollments = [
            ("STU1001", "CS101"),
            ("STU1001", "MA101"),
            ("STU1002", "CS101"),
            ("STU1002", "PH101"),
            ("STU1003", "EN101"),
            ("STU1004", "CS101"),
            ("STU1005", "CS201"),
            ("STU1005", "MA101")
        ]
        cursor.executemany("INSERT OR IGNORE INTO student_courses (student_id, course_code) VALUES (?, ?);", sample_enrollments)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
