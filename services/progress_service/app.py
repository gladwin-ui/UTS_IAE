from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import sys

# Add parent directory to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG, DATABASES

app = Flask(__name__)

# MySQL Database Configuration
db_config = DB_CONFIG.copy()
db_config['database'] = DATABASES['progress_service']

# Build connection string - handle empty password
if db_config['password']:
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"
else:
    connection_string = f"mysql+pymysql://{db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)
CORS(app)

# Models
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    enrollment_id = db.Column(db.Integer, nullable=False, index=True)
    module_id = db.Column(db.String(100))
    lesson_id = db.Column(db.String(100))
    completion_percentage = db.Column(db.Float, default=0.0)
    time_spent_minutes = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='in_progress', index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrollment_id': self.enrollment_id,
            'module_id': self.module_id,
            'lesson_id': self.lesson_id,
            'completion_percentage': self.completion_percentage,
            'time_spent_minutes': self.time_spent_minutes,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Module(db.Model):
    """Course Modules - Learning modules for each course"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)  # For ordering modules
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Task(db.Model):
    """Course Tasks - Tasks provided by course, not created by students"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50), default='assignment')  # assignment, quiz, project, exam, etc.
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    points = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)  # For ordering tasks
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'points': self.points,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserTaskCompletion(db.Model):
    """Track which tasks are completed by which users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(50), default='pending', index=True)  # pending, in_progress, completed
    completed_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='unique_user_task'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'course_id': self.course_id,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Submission(db.Model):
    """Task submissions by students"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    submission_text = db.Column(db.Text)  # Text submission
    submission_file_url = db.Column(db.String(500))  # URL to uploaded file
    submission_file_name = db.Column(db.String(200))  # Original filename
    status = db.Column(db.String(50), default='submitted', index=True)  # submitted, graded, returned
    grade = db.Column(db.Float, nullable=True)  # Grade/score
    feedback = db.Column(db.Text)  # Instructor feedback
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    graded_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'course_id': self.course_id,
            'submission_text': self.submission_text,
            'submission_file_url': self.submission_file_url,
            'submission_file_name': self.submission_file_name,
            'status': self.status,
            'grade': self.grade,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Routes
@app.route('/api/progress', methods=['GET'])
def get_progress():
    user_id = request.args.get('user_id')
    course_id = request.args.get('course_id')
    enrollment_id = request.args.get('enrollment_id')
    
    query = Progress.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if enrollment_id:
        query = query.filter_by(enrollment_id=enrollment_id)
    
    progress_records = query.all()
    return jsonify([progress.to_dict() for progress in progress_records]), 200

@app.route('/api/progress/<int:progress_id>', methods=['GET'])
def get_progress_record(progress_id):
    progress = Progress.query.get_or_404(progress_id)
    return jsonify(progress.to_dict()), 200

@app.route('/api/progress', methods=['POST'])
def create_progress():
    data = request.get_json()
    
    progress = Progress(
        user_id=data.get('user_id'),
        course_id=data.get('course_id'),
        enrollment_id=data.get('enrollment_id'),
        module_id=data.get('module_id'),
        lesson_id=data.get('lesson_id'),
        completion_percentage=data.get('completion_percentage', 0.0),
        time_spent_minutes=data.get('time_spent_minutes', 0.0),
        status=data.get('status', 'in_progress')
    )
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'message': 'Progress created successfully',
        'progress': progress.to_dict()
    }), 201

@app.route('/api/progress/<int:progress_id>', methods=['PUT'])
def update_progress(progress_id):
    progress = Progress.query.get_or_404(progress_id)
    data = request.get_json()
    
    progress.module_id = data.get('module_id', progress.module_id)
    progress.lesson_id = data.get('lesson_id', progress.lesson_id)
    progress.completion_percentage = data.get('completion_percentage', progress.completion_percentage)
    progress.time_spent_minutes = data.get('time_spent_minutes', progress.time_spent_minutes)
    progress.status = data.get('status', progress.status)
    progress.last_accessed = datetime.utcnow()
    
    if data.get('completed_at'):
        progress.completed_at = datetime.fromisoformat(data.get('completed_at'))
    elif progress.completion_percentage >= 100.0:
        progress.status = 'completed'
        progress.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progress updated successfully',
        'progress': progress.to_dict()
    }), 200

@app.route('/api/progress/user/<int:user_id>/course/<int:course_id>', methods=['GET'])
def get_user_course_progress(user_id, course_id):
    progress_records = Progress.query.filter_by(user_id=user_id, course_id=course_id).all()
    
    if not progress_records:
        return jsonify({
            'user_id': user_id,
            'course_id': course_id,
            'overall_completion': 0.0,
            'total_time_spent': 0.0,
            'status': 'not_started',
            'progress_records': []
        }), 200
    
    overall_completion = sum(p.completion_percentage for p in progress_records) / len(progress_records)
    total_time_spent = sum(p.time_spent_minutes for p in progress_records)
    status = 'completed' if all(p.status == 'completed' for p in progress_records) else 'in_progress'
    
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'overall_completion': round(overall_completion, 2),
        'total_time_spent': round(total_time_spent, 2),
        'status': status,
        'progress_records': [p.to_dict() for p in progress_records]
    }), 200

# Module Routes - Course Modules
@app.route('/api/modules', methods=['GET'])
def get_modules():
    """Get course modules"""
    course_id = request.args.get('course_id')
    
    query = Module.query
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    modules = query.order_by(Module.order_index.asc()).all()
    return jsonify([module.to_dict() for module in modules]), 200

@app.route('/api/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    """Get module by ID"""
    module = Module.query.get_or_404(module_id)
    return jsonify(module.to_dict()), 200

# Task Routes - Course Tasks (provided by course)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get course tasks (not user-specific)"""
    course_id = request.args.get('course_id')
    
    query = Task.query
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    
    tasks = query.order_by(Task.order_index.asc(), Task.due_date.asc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create course task (only instructor/admin can do this)"""
    data = request.get_json()
    
    task = Task(
        course_id=data.get('course_id'),
        title=data.get('title'),
        description=data.get('description'),
        task_type=data.get('task_type', 'assignment'),
        due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
        priority=data.get('priority', 'medium'),
        points=data.get('points', 0),
        order_index=data.get('order_index', 0)
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update course task (only instructor/admin can do this)"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.task_type = data.get('task_type', task.task_type)
    task.priority = data.get('priority', task.priority)
    task.points = data.get('points', task.points)
    task.order_index = data.get('order_index', task.order_index)
    task.updated_at = datetime.utcnow()
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data.get('due_date'))
    
    db.session.commit()
    
    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/api/tasks/user/<int:user_id>/course/<int:course_id>', methods=['GET'])
def get_user_course_tasks(user_id, course_id):
    """Get course tasks with user completion status"""
    # Get all tasks for the course
    course_tasks = Task.query.filter_by(course_id=course_id).order_by(
        Task.order_index.asc(), Task.due_date.asc()
    ).all()
    
    # Get user completions
    completions = UserTaskCompletion.query.filter_by(
        user_id=user_id, course_id=course_id
    ).all()
    completion_map = {c.task_id: c for c in completions}
    
    # Combine tasks with user completion status
    tasks_with_status = []
    for task in course_tasks:
        task_dict = task.to_dict()
        completion = completion_map.get(task.id)
        if completion:
            task_dict['user_status'] = completion.status
            task_dict['completed_at'] = completion.completed_at.isoformat() if completion.completed_at else None
        else:
            task_dict['user_status'] = 'pending'
            task_dict['completed_at'] = None
        tasks_with_status.append(task_dict)
    
    completed_count = len([t for t in tasks_with_status if t['user_status'] == 'completed'])
    
    return jsonify({
        'user_id': user_id,
        'course_id': course_id,
        'total_tasks': len(tasks_with_status),
        'completed_tasks': completed_count,
        'pending_tasks': len(tasks_with_status) - completed_count,
        'tasks': tasks_with_status
    }), 200

# User Task Completion Routes
@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark task as completed by user"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    task = Task.query.get_or_404(task_id)
    
    # Check if completion already exists
    completion = UserTaskCompletion.query.filter_by(
        user_id=user_id, task_id=task_id
    ).first()
    
    if completion:
        completion.status = 'completed'
        completion.completed_at = datetime.utcnow()
        completion.updated_at = datetime.utcnow()
    else:
        completion = UserTaskCompletion(
            user_id=user_id,
            task_id=task_id,
            course_id=task.course_id,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(completion)
    
    db.session.commit()
    
    # Update progress based on completed tasks
    update_progress_from_tasks(user_id, task.course_id)
    
    return jsonify({
        'message': 'Task marked as completed',
        'completion': completion.to_dict()
    }), 200

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update user task status (pending, in_progress, completed)"""
    data = request.get_json()
    user_id = data.get('user_id')
    status = data.get('status')
    
    if not user_id or not status:
        return jsonify({'error': 'user_id and status are required'}), 400
    
    if status not in ['pending', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    task = Task.query.get_or_404(task_id)
    
    completion = UserTaskCompletion.query.filter_by(
        user_id=user_id, task_id=task_id
    ).first()
    
    if completion:
        completion.status = status
        if status == 'completed':
            completion.completed_at = datetime.utcnow()
        else:
            completion.completed_at = None
        completion.updated_at = datetime.utcnow()
    else:
        completion = UserTaskCompletion(
            user_id=user_id,
            task_id=task_id,
            course_id=task.course_id,
            status=status,
            completed_at=datetime.utcnow() if status == 'completed' else None
        )
        db.session.add(completion)
    
    db.session.commit()
    
    # Update progress based on completed tasks
    if status == 'completed':
        update_progress_from_tasks(user_id, task.course_id)
    
    return jsonify({
        'message': 'Task status updated',
        'completion': completion.to_dict()
    }), 200

def update_progress_from_tasks(user_id, course_id):
    """Update progress percentage based on completed tasks"""
    # Get all tasks for course
    total_tasks = Task.query.filter_by(course_id=course_id).count()
    
    if total_tasks == 0:
        return
    
    # Get completed tasks
    completed_tasks = UserTaskCompletion.query.filter_by(
        user_id=user_id,
        course_id=course_id,
        status='completed'
    ).count()
    
    # Calculate completion percentage
    completion_percentage = (completed_tasks / total_tasks) * 100
    
    # Get or create progress record
    progress_records = Progress.query.filter_by(
        user_id=user_id, course_id=course_id
    ).all()
    
    # Get enrollment_id if exists
    enrollment_id = 0
    try:
        import requests
        from config import SERVICES
        enrollment_response = requests.get(
            f"{SERVICES['enrollment']}/api/enrollments",
            params={'user_id': user_id, 'course_id': course_id},
            timeout=5
        )
        if enrollment_response.ok:
            enrollments = enrollment_response.json()
            if enrollments:
                enrollment_id = enrollments[0].get('id', 0)
    except:
        pass
    
    if progress_records:
        for progress in progress_records:
            progress.completion_percentage = completion_percentage
            if enrollment_id > 0:
                progress.enrollment_id = enrollment_id
            if completion_percentage >= 100:
                progress.status = 'completed'
                progress.completed_at = datetime.utcnow()
            else:
                progress.status = 'in_progress'
            progress.last_accessed = datetime.utcnow()
    else:
        progress = Progress(
            user_id=user_id,
            course_id=course_id,
            enrollment_id=enrollment_id,
            completion_percentage=completion_percentage,
            status='completed' if completion_percentage >= 100 else 'in_progress'
        )
        db.session.add(progress)
    
    db.session.commit()

# Submission Routes
@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get submissions with filters"""
    user_id = request.args.get('user_id')
    task_id = request.args.get('task_id')
    course_id = request.args.get('course_id')
    status = request.args.get('status')
    
    query = Submission.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if task_id:
        query = query.filter_by(task_id=task_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if status:
        query = query.filter_by(status=status)
    
    submissions = query.order_by(Submission.submitted_at.desc()).all()
    return jsonify([submission.to_dict() for submission in submissions]), 200

@app.route('/api/submissions/<int:submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Get submission by ID"""
    submission = Submission.query.get_or_404(submission_id)
    return jsonify(submission.to_dict()), 200

@app.route('/api/submissions', methods=['POST'])
def create_submission():
    """Create new submission"""
    data = request.get_json()
    
    # Check if submission already exists for this user and task
    existing = Submission.query.filter_by(
        user_id=data.get('user_id'),
        task_id=data.get('task_id')
    ).first()
    
    if existing:
        return jsonify({'error': 'Submission already exists for this task'}), 400
    
    submission = Submission(
        user_id=data.get('user_id'),
        task_id=data.get('task_id'),
        course_id=data.get('course_id'),
        submission_text=data.get('submission_text'),
        submission_file_url=data.get('submission_file_url'),
        submission_file_name=data.get('submission_file_name'),
        status='submitted'
    )
    
    db.session.add(submission)
    
    # Update task completion status
    completion = UserTaskCompletion.query.filter_by(
        user_id=data.get('user_id'),
        task_id=data.get('task_id')
    ).first()
    
    if completion:
        completion.status = 'completed'
        completion.submitted_at = datetime.utcnow()
        completion.completed_at = datetime.utcnow()
    else:
        completion = UserTaskCompletion(
            user_id=data.get('user_id'),
            task_id=data.get('task_id'),
            course_id=data.get('course_id'),
            status='completed',
            submitted_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.session.add(completion)
    
    db.session.commit()
    
    # Update progress
    update_progress_from_tasks(data.get('user_id'), data.get('course_id'))
    
    return jsonify({
        'message': 'Submission created successfully',
        'submission': submission.to_dict()
    }), 201

@app.route('/api/submissions/<int:submission_id>', methods=['PUT'])
def update_submission(submission_id):
    """Update submission (for resubmission or grading)"""
    submission = Submission.query.get_or_404(submission_id)
    data = request.get_json()
    
    submission.submission_text = data.get('submission_text', submission.submission_text)
    submission.submission_file_url = data.get('submission_file_url', submission.submission_file_url)
    submission.submission_file_name = data.get('submission_file_name', submission.submission_file_name)
    submission.status = data.get('status', submission.status)
    submission.grade = data.get('grade', submission.grade)
    submission.feedback = data.get('feedback', submission.feedback)
    submission.updated_at = datetime.utcnow()
    
    if data.get('grade') is not None:
        submission.graded_at = datetime.utcnow()
        submission.status = 'graded'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Submission updated successfully',
        'submission': submission.to_dict()
    }), 200

@app.route('/api/submissions/user/<int:user_id>/task/<int:task_id>', methods=['GET'])
def get_user_task_submission(user_id, task_id):
    """Get user's submission for a specific task"""
    submission = Submission.query.filter_by(
        user_id=user_id,
        task_id=task_id
    ).first()
    
    if not submission:
        return jsonify({'message': 'No submission found', 'submission': None}), 200
    
    return jsonify(submission.to_dict()), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'progress_service'}), 200

@app.route('/api/tasks/initialize', methods=['POST'])
def initialize_tasks_endpoint():
    """Endpoint to manually initialize sample tasks"""
    try:
        initialize_sample_tasks()
        task_count = Task.query.count()
        return jsonify({
            'message': 'Sample tasks initialized successfully',
            'total_tasks': task_count
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Error initializing tasks: {str(e)}'
        }), 500

def initialize_sample_modules():
    """Create sample modules for existing courses"""
    try:
        # Sample modules for each course
        course_modules = {
            1: [  # Python Programming Basics
                {'title': 'Pengenalan Python', 'description': 'Pelajari dasar-dasar bahasa pemrograman Python, termasuk instalasi, sintaks dasar, dan cara menjalankan program Python pertama Anda.', 'order_index': 1},
                {'title': 'Variabel dan Tipe Data', 'description': 'Pahami berbagai tipe data dalam Python seperti integer, float, string, list, dan dictionary serta cara menggunakannya.', 'order_index': 2},
                {'title': 'Struktur Kontrol', 'description': 'Pelajari penggunaan if-else, loop (for dan while), dan cara mengontrol alur program dengan struktur kontrol.', 'order_index': 3},
                {'title': 'Fungsi dan Modul', 'description': 'Belajar membuat fungsi, menggunakan parameter, return value, dan cara mengorganisir kode dengan modul.', 'order_index': 4},
                {'title': 'Object-Oriented Programming', 'description': 'Pahami konsep OOP dalam Python termasuk class, object, inheritance, dan polymorphism.', 'order_index': 5}
            ],
            2: [  # Advanced Web Development
                {'title': 'HTML & CSS Fundamentals', 'description': 'Pelajari dasar-dasar HTML5 dan CSS3 untuk membuat struktur dan styling halaman web yang responsif.', 'order_index': 1},
                {'title': 'JavaScript Essentials', 'description': 'Pahami JavaScript modern termasuk ES6+, DOM manipulation, event handling, dan asynchronous programming.', 'order_index': 2},
                {'title': 'React Basics', 'description': 'Pelajari React framework termasuk komponen, props, state, hooks, dan cara membangun aplikasi React modern.', 'order_index': 3},
                {'title': 'Node.js & Express', 'description': 'Belajar membangun backend dengan Node.js dan Express, termasuk routing, middleware, dan API development.', 'order_index': 4},
                {'title': 'Full Stack Integration', 'description': 'Integrasikan frontend React dengan backend Node.js untuk membuat aplikasi full stack yang lengkap.', 'order_index': 5}
            ],
            3: [  # Machine Learning Fundamentals
                {'title': 'Pengenalan Data Science', 'description': 'Pelajari dasar-dasar data science, analisis data dengan pandas, dan visualisasi data menggunakan matplotlib dan seaborn.', 'order_index': 1},
                {'title': 'Data Preprocessing', 'description': 'Pahami teknik preprocessing data termasuk handling missing values, normalisasi, encoding, dan feature engineering.', 'order_index': 2},
                {'title': 'Konsep Machine Learning', 'description': 'Pelajari konsep supervised vs unsupervised learning, overfitting, underfitting, dan teknik evaluasi model.', 'order_index': 3},
                {'title': 'Algoritma Machine Learning', 'description': 'Pahami berbagai algoritma ML seperti linear regression, decision tree, random forest, dan neural networks.', 'order_index': 4},
                {'title': 'Model Evaluation & Deployment', 'description': 'Pelajari cara mengevaluasi model ML, hyperparameter tuning, dan cara deploy model ke production.', 'order_index': 5}
            ]
        }
        
        for course_id, modules in course_modules.items():
            for module_data in modules:
                # Check if module already exists
                existing = Module.query.filter_by(
                    course_id=course_id,
                    title=module_data['title']
                ).first()
                
                if not existing:
                    module = Module(
                        course_id=course_id,
                        title=module_data['title'],
                        description=module_data['description'],
                        order_index=module_data['order_index']
                    )
                    db.session.add(module)
        
        db.session.commit()
        print("[OK] Sample modules created for courses")
    except Exception as e:
        print(f"[WARNING] Error creating sample modules: {e}")
        db.session.rollback()

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
        
        for course_id, tasks in course_tasks.items():
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
        
        db.session.commit()
        print("[OK] Sample tasks created for courses")
    except Exception as e:
        print(f"[WARNING] Error creating sample tasks: {e}")
        db.session.rollback()

if __name__ == '__main__':
    print("=" * 60)
    print("Progress Service Starting...")
    print("=" * 60)
    
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database initialized")
            initialize_sample_modules()
            initialize_sample_tasks()
        except Exception as e:
            print(f"[WARNING] Error initializing database: {e}")
            print("Service will continue running, but database operations may fail.")
    
    print("\nStarting Progress Service on port 5004...")
    print("=" * 60)
    try:
        app.run(port=5004, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
