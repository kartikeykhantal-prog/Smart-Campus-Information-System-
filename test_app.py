import unittest
import sys
import os

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import algorithms

class TestCampusAlgorithms(unittest.TestCase):

    def test_evaluate_grade(self):
        # Test A
        g, r = algorithms.evaluate_grade(95.0)
        self.assertEqual(g, 'A')
        self.assertIn('Excellent', r)
        
        # Test B
        g, r = algorithms.evaluate_grade(84)
        self.assertEqual(g, 'B')
        self.assertIn('Good', r)
        
        # Test C
        g, r = algorithms.evaluate_grade(72.5)
        self.assertEqual(g, 'C')
        self.assertIn('Satisfactory', r)
        
        # Test D
        g, r = algorithms.evaluate_grade("65.5")
        self.assertEqual(g, 'D')
        self.assertIn('Pass', r)
        
        # Test F
        g, r = algorithms.evaluate_grade(45)
        self.assertEqual(g, 'F')
        self.assertIn('Failed', r)
        
        # Test invalid inputs
        g, r = algorithms.evaluate_grade("invalid_marks")
        self.assertEqual(g, 'F')
        self.assertEqual(r, 'Invalid score')

    def test_calculate_total_fee(self):
        # Normal inputs
        total = algorithms.calculate_total_fee(8000, 1500, 500)
        self.assertEqual(total, 10000.0)
        
        # Floating point / string support
        total = algorithms.calculate_total_fee("6000.50", "1200", 250)
        self.assertEqual(total, 7450.50)
        
        # None inputs
        total = algorithms.calculate_total_fee(5000, None, 300)
        self.assertEqual(total, 5300.0)
        
        # Invalid numeric inputs
        total = algorithms.calculate_total_fee("invalid", 1000, 200)
        self.assertEqual(total, 0.0)

    def test_bubble_sort(self):
        students = [
            {"student_id": "STU1003", "name": "Charlie", "score": 75},
            {"student_id": "STU1001", "name": "Alice", "score": 95},
            {"student_id": "STU1002", "name": "Bob", "score": 85}
        ]
        
        # Sort Ascending by ID
        sorted_asc = algorithms.bubble_sort(students, key='student_id', reverse=False)
        self.assertEqual(sorted_asc[0]['student_id'], 'STU1001')
        self.assertEqual(sorted_asc[2]['student_id'], 'STU1003')
        
        # Sort Descending by ID
        sorted_desc = algorithms.bubble_sort(students, key='student_id', reverse=True)
        self.assertEqual(sorted_desc[0]['student_id'], 'STU1003')
        self.assertEqual(sorted_desc[2]['student_id'], 'STU1001')
        
        # Sort by score descending (high to low)
        sorted_score = algorithms.bubble_sort(students, key='score', reverse=True)
        self.assertEqual(sorted_score[0]['name'], 'Alice')
        self.assertEqual(sorted_score[2]['name'], 'Charlie')

    def test_linear_search(self):
        students = [
            {"student_id": "STU1001", "name": "Alice"},
            {"student_id": "STU1002", "name": "Bob"},
            {"student_id": "STU1003", "name": "Charlie"}
        ]
        
        # Search found case
        found, steps = algorithms.linear_search(students, "STU1002")
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'Bob')
        self.assertEqual(len(steps), 2) # STU1001 and STU1002 checked
        
        # Search missing case
        found, steps = algorithms.linear_search(students, "STU1009")
        self.assertIsNone(found)
        self.assertEqual(len(steps), 3) # Checked all 3

    def test_binary_search(self):
        students = [
            {"student_id": "STU1003", "name": "Charlie"},
            {"student_id": "STU1001", "name": "Alice"},
            {"student_id": "STU1002", "name": "Bob"}
        ]
        
        # Search found case (binary_search automatically sorts by ID first!)
        found, steps = algorithms.binary_search(students, "STU1003")
        self.assertIsNotNone(found)
        self.assertEqual(found['name'], 'Charlie')
        self.assertTrue(len(steps) > 0)
        
        # Search missing case
        found, steps = algorithms.binary_search(students, "STU1009")
        self.assertIsNone(found)

if __name__ == '__main__':
    unittest.main()
