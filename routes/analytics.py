from flask import Blueprint, jsonify, current_app
import database
import os
import pandas as pd
import matplotlib
# Use the non-interactive Agg backend to avoid GUI issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, score, grade, total_fee FROM students;")
        rows = cursor.fetchall()
        conn.close()
        
        # Check if empty database
        if not rows:
            return jsonify({
                "has_data": False,
                "total_students": 0,
                "mean": 0,
                "median": 0,
                "max": 0,
                "min": 0,
                "top_performers": [],
                "grade_distribution": {},
                "chart_url": None
            })
            
        # Load into Pandas DataFrame
        df = pd.DataFrame([dict(r) for r in rows])
        
        # Calculate summary statistics using Pandas
        total_students = int(df.shape[0])
        mean_score = float(df['score'].mean())
        median_score = float(df['score'].median())
        max_score = float(df['score'].max())
        min_score = float(df['score'].min())
        
        # Sort values to find top performers (top 3)
        top_performers_df = df.sort_values(by='score', ascending=False).head(3)
        top_performers = top_performers_df[['name', 'score', 'grade']].to_dict(orient='records')
        
        # Get Grade counts
        grade_distribution = df['grade'].value_counts().to_dict()
        # Make sure all grades are present in dict for consistency
        for g in ['A', 'B', 'C', 'D', 'F']:
            if g not in grade_distribution:
                grade_distribution[g] = 0
                
        # Draw analytics chart using Matplotlib
        chart_dir = os.path.join(current_app.root_path, 'static', 'plots')
        os.makedirs(chart_dir, exist_ok=True)
        chart_path = os.path.join(chart_dir, 'analytics.png')
        
        # Setup modern dark style for the matplotlib chart
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
        fig.patch.set_facecolor('#0f172a') # Matching dashboard dark blue (#0f172a)
        
        # Panel 1: Grade Distribution (Bar Chart)
        grades_ordered = ['A', 'B', 'C', 'D', 'F']
        counts = [grade_distribution[g] for g in grades_ordered]
        
        bars1 = ax1.bar(grades_ordered, counts, color=['#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef', '#ef4444'], width=0.6, edgecolor='none')
        ax1.set_title('Grade Distribution', color='#f8fafc', fontsize=12, pad=10)
        ax1.set_ylabel('Number of Students', color='#94a3b8')
        ax1.tick_params(colors='#94a3b8')
        ax1.yaxis.get_major_locator().set_params(integer=True)
        ax1.set_facecolor('#1e293b') # Dark card background
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#475569')
        ax1.spines['bottom'].set_color('#475569')
        
        # Add labels to bars
        for bar in bars1:
            yval = bar.get_height()
            if yval > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{int(yval)}", 
                         ha='center', va='bottom', color='#f8fafc', fontweight='bold')
        
        # Panel 2: Student Scores (Bar Chart for Top 5 students)
        top5_df = df.sort_values(by='score', ascending=False).head(5)
        names_short = [n.split()[0] if len(n.split()) > 0 else n for n in top5_df['name']]
        
        bars2 = ax2.bar(names_short, top5_df['score'], color='#06b6d4', width=0.5, alpha=0.85)
        ax2.set_title('Top Students Performance', color='#f8fafc', fontsize=12, pad=10)
        ax2.set_ylabel('Score (%)', color='#94a3b8')
        ax2.tick_params(colors='#94a3b8')
        ax2.set_ylim(0, 110)
        ax2.set_facecolor('#1e293b')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#475569')
        ax2.spines['bottom'].set_color('#475569')
        
        for bar in bars2:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", 
                     ha='center', va='bottom', color='#06b6d4', fontsize=9, fontweight='bold')
            
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        return jsonify({
            "has_data": True,
            "total_students": total_students,
            "mean": round(mean_score, 2),
            "median": round(median_score, 2),
            "max": round(max_score, 2),
            "min": round(min_score, 2),
            "top_performers": top_performers,
            "grade_distribution": grade_distribution,
            "chart_url": "/static/plots/analytics.png"
        })
        
    except Exception as e:
        return jsonify({"error": f"Analytics failed: {str(e)}"}), 500
