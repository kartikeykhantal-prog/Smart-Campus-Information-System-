# Smart Campus Information System

A full-stack, responsive, and interactive campus dashboard application built with **Python Flask** and stylized with a premium glassmorphic dark theme dashboard.

---

## Features Implemented

1. **Student Registration & Grade Evaluation**: Form input with auto A-F grade mapping and performance remark evaluator.
2. **Course Enrollment Manager**: Add/Delete courses and enroll students. Limits validation (max 5 courses, max 18 total credits per student).
3. **Student Records**: Stores students, grades, fees, and course lists in SQLite. Renders in a dynamic table.
4. **Search & Sorting**: Custom Bubble Sort (ascending/descending) on ID or Score. Linear & Binary search tracer highlighting comparison steps.
5. **Fee Calculator**: Reusable fee calculation model for Tuition, Hostel, and Transport.
6. **File Backups**: Backup database to a downloadable JSON file, or restore database by uploading a backup JSON.
7. **Directory Scanner**: Recursive tree view generator for server folder structures with custom Exception Logs.
8. **Performance Analytics**: Pandas aggregations (Mean, Median, Min, Max, Top Performers) and Matplotlib charts.

---

## Folder Structure

```
smart-campus/
├── app.py                      # Flask Server Entrypoint
├── database.py                 # SQLite Schema Setup & Seed Data
├── algorithms.py               # Reusable Algorithms (Grading, Fee, Sorts, Searches)
├── requirements.txt            # Python Dependencies
├── test_app.py                 # Python Unittests Suite
├── data/
│   └── campus.db               # SQLite Local Database (auto-generated)
├── routes/
│   ├── __init__.py             # Blueprint exports
│   ├── student.py              # Students REST APIs & Searches
│   ├── course.py               # Courses CRUD & Enrollments
│   ├── fee.py                  # Fee Calculations & Upgrades
│   ├── scanner.py              # Folder trees & exception handlers
│   └── analytics.py            # Pandas + Matplotlib charts compiler
├── templates/
│   ├── base.html               # Master Layout Frame (Sidebar navigation header)
│   └── index.html              # Main Dashboard panels and templates
└── static/
    ├── css/
    │   └── styles.css          # Glassmorphic Card CSS Theme
    ├── js/
    │   └── app.js              # Routing, client-side preview calculations, algorithms visual traces
    └── plots/
        └── analytics.png       # Matplotlib-rendered charts (auto-generated)
```

---

## Setup & Running Instructions

### Prerequisites
- Python 3.10+ installed and added to your system PATH.

### 1. Install Dependencies
In your terminal, navigate to the `smart-campus` directory and run:
```bash
pip install -r requirements.txt
```

### 2. Run the Unit Tests
To verify all calculations, grading logic, sorting, and search algorithms:
```bash
python3 test_app.py
```

### 3. Start the Flask Server
Launch the application:
```bash
python3 app.py
```

The server will initialize the local database schema with seed values and start listening on:
`http://127.0.0.1:5000/`

Open this URL in your web browser to interact with the dashboard.
- Navigating the sidebar toggles tab cards.
- Try **Directory Scanner** by typing local paths or leaving it empty to scan the project files.
