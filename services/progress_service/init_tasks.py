#!/usr/bin/env python3
"""
Script to manually initialize sample tasks for courses
Run this script to ensure tasks are created in the database
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG, DATABASES

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# MySQL Database Configuration
db_config = DB_CONFIG.copy()
db_config['database'] = DATABASES['progress_service']

# Build connection string
if db_config['password']:
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"
else:
    connection_string = f"mysql+pymysql://{db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import Task model
class Task(db.Model):
    """Course Tasks - Tasks provided by course, not created by students"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50), default='assignment')
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')
    points = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

def initialize_sample_tasks():
    """Create sample tasks for existing courses"""
    try:
        # Sample tasks for each course
        course_tasks = {
            1: [  # Python Programming Basics
                {'title': 'Introduction to Python Syntax', 'description': 'Write a Python program that prints "Hello, World!" and demonstrates basic variable usage.', 'task_type': 'assignment', 'priority': 'low', 'points': 10, 'order_index': 1},
                {'title': 'Variables and Data Types', 'description': 'Create a program that uses different data types (int, float, string, list) and print their types.', 'task_type': 'assignment', 'priority': 'low', 'points': 15, 'order_index': 2},
                {'title': 'Control Structures Quiz', 'description': 'Complete a quiz on if-else statements, loops, and control flow in Python.', 'task_type': 'quiz', 'priority': 'medium', 'points': 20, 'order_index': 3},
                {'title': 'Functions and Modules', 'description': 'Create a module with at least 3 functions and demonstrate their usage in a main program.', 'task_type': 'assignment', 'priority': 'medium', 'points': 25, 'order_index': 4},
                {'title': 'Final Project: Calculator', 'description': 'Build a simple calculator program that can perform basic arithmetic operations.', 'task_type': 'project', 'priority': 'high', 'points': 30, 'order_index': 5}
            ],
            2: [  # Advanced Web Development
                {'title': 'HTML/CSS Basics', 'description': 'Create a responsive webpage using HTML5 and CSS3 with a navigation bar and footer.', 'task_type': 'assignment', 'priority': 'low', 'points': 15, 'order_index': 1},
                {'title': 'JavaScript Fundamentals', 'description': 'Write JavaScript code to handle DOM manipulation and event listeners.', 'task_type': 'assignment', 'priority': 'medium', 'points': 20, 'order_index': 2},
                {'title': 'React Components Quiz', 'description': 'Complete a quiz on React components, props, and state management.', 'task_type': 'quiz', 'priority': 'medium', 'points': 25, 'order_index': 3},
                {'title': 'Node.js API Development', 'description': 'Build a RESTful API using Node.js and Express with CRUD operations.', 'task_type': 'project', 'priority': 'high', 'points': 35, 'order_index': 4},
                {'title': 'Full Stack Application', 'description': 'Create a complete full-stack application with React frontend and Node.js backend.', 'task_type': 'project', 'priority': 'high', 'points': 50, 'order_index': 5}
            ],
            3: [  # Machine Learning Fundamentals
                {'title': 'Introduction to Data Science', 'description': 'Analyze a dataset using pandas and create visualizations with matplotlib.', 'task_type': 'assignment', 'priority': 'low', 'points': 20, 'order_index': 1},
                {'title': 'Data Preprocessing', 'description': 'Clean and preprocess a dataset: handle missing values, normalize data, and feature engineering.', 'task_type': 'assignment', 'priority': 'medium', 'points': 25, 'order_index': 2},
                {'title': 'Machine Learning Concepts Quiz', 'description': 'Complete a quiz on supervised vs unsupervised learning, overfitting, and model evaluation.', 'task_type': 'quiz', 'priority': 'medium', 'points': 30, 'order_index': 3},
                {'title': 'Linear Regression Model', 'description': 'Implement a linear regression model from scratch and evaluate its performance.', 'task_type': 'project', 'priority': 'high', 'points': 40, 'order_index': 4},
                {'title': 'Final ML Project', 'description': 'Build a complete machine learning pipeline: data collection, preprocessing, model training, and evaluation.', 'task_type': 'project', 'priority': 'high', 'points': 50, 'order_index': 5}
            ]
        }
        
        created_count = 0
        for course_id, tasks in course_tasks.items():
            print(f"\nProcessing course_id {course_id}...")
            for task_data in tasks:
                # Check if task already exists
                existing = Task.query.filter_by(
                    course_id=course_id,
                    title=task_data['title']
                ).first()
                
                if not existing:
                    task = Task(
                        course_id=course_id,
                        title=task_data['title'],
                        description=task_data['description'],
                        task_type=task_data['task_type'],
                        priority=task_data['priority'],
                        points=task_data['points'],
                        order_index=task_data['order_index']
                    )
                    db.session.add(task)
                    created_count += 1
                    print(f"  [OK] Created: {task_data['title']}")
                else:
                    print(f"  [-] Already exists: {task_data['title']}")
        
        db.session.commit()
        print(f"\n[OK] Sample tasks created: {created_count} new tasks")
        print(f"[OK] Total tasks in database: {Task.query.count()}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating sample tasks: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Initializing Sample Tasks")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Create all tables (this will add missing columns)
            db.create_all()
            print("[OK] Database connection established")
            
            # Check and fix table structure
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('task')]
                
                # Add order_index if missing
                if 'order_index' not in columns:
                    print("[INFO] Adding order_index column to task table...")
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE task ADD COLUMN order_index INT DEFAULT 0"))
                        conn.commit()
                    print("[OK] order_index column added")
                
                # Remove user_id if exists (tasks are now course-provided, not user-created)
                if 'user_id' in columns:
                    print("[INFO] Removing user_id column from task table (tasks are course-provided)...")
                    with db.engine.connect() as conn:
                        # Check if there are foreign key constraints
                        try:
                            conn.execute(text("ALTER TABLE task DROP FOREIGN KEY IF EXISTS task_ibfk_1"))
                        except:
                            pass
                        try:
                            conn.execute(text("ALTER TABLE task DROP COLUMN user_id"))
                        except Exception as e:
                            print(f"[WARNING] Could not drop user_id column: {e}")
                        conn.commit()
                    print("[OK] user_id column removed")
            except Exception as e:
                print(f"[WARNING] Could not check/fix table structure: {e}")
            
            if initialize_sample_tasks():
                print("\n[SUCCESS] Tasks initialization completed!")
            else:
                print("\n[FAILED] Tasks initialization failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] Fatal error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

