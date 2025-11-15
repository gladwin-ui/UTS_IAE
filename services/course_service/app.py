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
db_config['database'] = DATABASES['course_service']

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
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, nullable=False, index=True)
    category = db.Column(db.String(100), index=True)
    price = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Float, default=0.0)
    level = db.Column(db.String(50), default='beginner')
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructor_id': self.instructor_id,
            'category': self.category,
            'price': self.price,
            'duration_hours': self.duration_hours,
            'level': self.level,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Routes
@app.route('/api/courses', methods=['GET'])
def get_courses():
    category = request.args.get('category')
    level = request.args.get('level')
    instructor_id = request.args.get('instructor_id')
    
    query = Course.query
    
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)
    
    courses = query.all()
    return jsonify([course.to_dict() for course in courses]), 200

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict()), 200

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    
    course = Course(
        title=data.get('title'),
        description=data.get('description'),
        instructor_id=data.get('instructor_id'),
        category=data.get('category'),
        price=data.get('price', 0.0),
        duration_hours=data.get('duration_hours', 0.0),
        level=data.get('level', 'beginner'),
        image_url=data.get('image_url')
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'message': 'Course created successfully',
        'course': course.to_dict()
    }), 201

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.category = data.get('category', course.category)
    course.price = data.get('price', course.price)
    course.duration_hours = data.get('duration_hours', course.duration_hours)
    course.level = data.get('level', course.level)
    course.image_url = data.get('image_url', course.image_url)
    course.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Course updated successfully',
        'course': course.to_dict()
    }), 200

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': 'Course deleted successfully'}), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'course_service'}), 200

def initialize_database():
    """Initialize database and create sample data"""
    try:
        db.create_all()
        
        # Course images mapping
        course_images = {
            'Python Programming Basics': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=600&fit=crop&q=80',
            'Advanced Web Development': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=600&fit=crop&q=80',
            'Machine Learning Fundamentals': 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600&fit=crop&q=80'
        }
        
        # Add sample courses
        if Course.query.count() == 0:
            sample_courses = [
                Course(
                    title='Python Programming Basics',
                    description='Learn the fundamentals of Python programming language',
                    instructor_id=1,
                    category='Programming',
                    price=49.99,
                    duration_hours=10.0,
                    level='beginner',
                    image_url=course_images['Python Programming Basics']
                ),
                Course(
                    title='Advanced Web Development',
                    description='Master modern web development with React and Node.js',
                    instructor_id=1,
                    category='Web Development',
                    price=79.99,
                    duration_hours=20.0,
                    level='intermediate',
                    image_url=course_images['Advanced Web Development']
                ),
                Course(
                    title='Machine Learning Fundamentals',
                    description='Introduction to machine learning and data science',
                    instructor_id=1,
                    category='Data Science',
                    price=99.99,
                    duration_hours=30.0,
                    level='advanced',
                    image_url=course_images['Machine Learning Fundamentals']
                ),
            ]
            for course in sample_courses:
                db.session.add(course)
            db.session.commit()
            print("[OK] Sample courses created successfully")
        else:
            print("[OK] Courses already exist")
            # Update existing courses with placeholder images
            updated_count = 0
            for title, image_url in course_images.items():
                course = Course.query.filter_by(title=title).first()
                if course and (not course.image_url or 'placeholder' in course.image_url.lower()):
                    course.image_url = image_url
                    updated_count += 1
            if updated_count > 0:
                db.session.commit()
                print(f"[OK] Updated {updated_count} course(s) with new images")
        return True
    except Exception as e:
        print(f"[WARNING] Error initializing database: {e}")
        print("Service will continue running, but database operations may fail.")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Course Service Starting...")
    print("=" * 60)
    
    with app.app_context():
        initialize_database()
    
    print("\nStarting Course Service on port 5002...")
    print("=" * 60)
    try:
        app.run(port=5002, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
