from .student import student_bp
from .course import course_bp
from .fee import fee_bp
from .scanner import scanner_bp
from .analytics import analytics_bp

# Expose them to make imports in app.py cleaner
__all__ = ['student_bp', 'course_bp', 'fee_bp', 'scanner_bp', 'analytics_bp']
