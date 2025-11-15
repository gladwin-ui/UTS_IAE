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
db_config['database'] = DATABASES['enrollment_service']

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
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    enrolled_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(50), default='active', index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# Routes
@app.route('/api/enrollments', methods=['GET'])
def get_enrollments():
    user_id = request.args.get('user_id')
    course_id = request.args.get('course_id')
    status = request.args.get('status')
    
    query = Enrollment.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if status:
        query = query.filter_by(status=status)
    
    enrollments = query.all()
    return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200

@app.route('/api/enrollments/<int:enrollment_id>', methods=['GET'])
def get_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    return jsonify(enrollment.to_dict()), 200

@app.route('/api/enrollments', methods=['POST'])
def create_enrollment():
    data = request.get_json()
    user_id = data.get('user_id')
    course_id = data.get('course_id')
    
    # Check if enrollment already exists
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'User is already enrolled in this course'}), 400
    
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        status=data.get('status', 'active')
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({
        'message': 'Enrollment created successfully',
        'enrollment': enrollment.to_dict()
    }), 201

@app.route('/api/enrollments/<int:enrollment_id>', methods=['PUT'])
def update_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    data = request.get_json()
    
    enrollment.status = data.get('status', enrollment.status)
    if data.get('completed_at'):
        enrollment.completed_at = datetime.fromisoformat(data.get('completed_at'))
    
    db.session.commit()
    
    return jsonify({
        'message': 'Enrollment updated successfully',
        'enrollment': enrollment.to_dict()
    }), 200

@app.route('/api/enrollments/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Enrollment deleted successfully'}), 200

@app.route('/api/enrollments/user/<int:user_id>/courses', methods=['GET'])
def get_user_enrolled_courses(user_id):
    enrollments = Enrollment.query.filter_by(user_id=user_id, status='active').all()
    course_ids = [enrollment.course_id for enrollment in enrollments]
    return jsonify({'course_ids': course_ids}), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'enrollment_service'}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Enrollment Service Starting...")
    print("=" * 60)
    
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database initialized")
        except Exception as e:
            print(f"[WARNING] Error initializing database: {e}")
            print("Service will continue running, but database operations may fail.")
    
    print("\nStarting Enrollment Service on port 5003...")
    print("=" * 60)
    try:
        app.run(port=5003, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
