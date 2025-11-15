from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
import sys

# Add parent directory to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG, DATABASES

app = Flask(__name__)

# MySQL Database Configuration
db_config = DB_CONFIG.copy()
db_config['database'] = DATABASES['user_service']

# Build connection string - handle empty password
if db_config['password']:
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"
else:
    # MySQL tanpa password
    connection_string = f"mysql+pymysql://{db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset={db_config['charset']}"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['JWT_SECRET_KEY'] = 'user-service-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(50), default='student')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Encrypt password menggunakan werkzeug
    password_hash = generate_password_hash(data.get('password'))
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        password_hash=password_hash,
        full_name=data.get('full_name'),
        role=data.get('role', 'student')
    )
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'token': access_token
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': access_token
    }), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@app.route('/api/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    user = User.query.get_or_404(user_id)
    
    # Authorization: user hanya bisa update dirinya sendiri, kecuali admin
    if current_user_id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized: You can only update your own profile'}), 403
    
    data = request.get_json()
    
    # Validasi dan update username (jika diubah)
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    # Validasi dan update email (jika diubah)
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    # Update field lainnya
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    # Hanya admin yang bisa mengubah role
    if 'role' in data:
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized: Only admin can change user role'}), 403
        user.role = data['role']
    
    # Update password (jika diubah)
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    user = User.query.get_or_404(user_id)
    
    # Authorization: user hanya bisa delete dirinya sendiri, kecuali admin
    if current_user_id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized: You can only delete your own account'}), 403
    
    # Prevent admin from deleting themselves
    if user.role == 'admin' and current_user_id == user_id:
        # Cek apakah ada admin lain
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return jsonify({'error': 'Cannot delete: At least one admin must exist'}), 400
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'user_service'}), 200

def initialize_database():
    """Initialize database and create default data"""
    try:
        # Test database connection first
        print("Testing database connection...")
        db.engine.connect()
        print("[OK] Database connection OK")
        
        # Create tables
        print("Creating tables...")
        db.create_all()
        print("[OK] Tables created/verified")
        
        # Create default test user if not exists
        if User.query.filter_by(username='admin').first() is None:
            default_user = User(
                username='admin',
                email='admin@educonnect.com',
                password_hash=generate_password_hash('admin123'),
                full_name='Administrator',
                role='admin'
            )
            db.session.add(default_user)
            db.session.commit()
            print("=" * 60)
            print("Default user created:")
            print("Username: admin")
            print("Password: admin123")
            print("=" * 60)
        
        # Create test student user
        if User.query.filter_by(username='student').first() is None:
            test_user = User(
                username='student',
                email='student@educonnect.com',
                password_hash=generate_password_hash('student123'),
                full_name='Test Student',
                role='student'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test student user created:")
            print("Username: student")
            print("Password: student123")
            print("=" * 60)
        
        print("[OK] User Service initialized successfully")
        return True
    except Exception as e:
        print("=" * 60)
        print("[WARNING] Failed to initialize database")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nService will continue running, but database operations may fail.")
        print("Troubleshooting:")
        print("1. Pastikan MySQL server running")
        print("2. Cek file .env dan pastikan DB_PASSWORD benar (kosong jika MySQL tanpa password)")
        print("3. Pastikan database sudah dibuat (jalankan: python setup_database.py)")
        print("=" * 60)
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("User Service Starting...")
    print("=" * 60)
    
    # Initialize database (non-blocking - service will run even if DB init fails)
    with app.app_context():
        initialize_database()
    
    print("\nStarting User Service on port 5001...")
    print("=" * 60)
    print("Service is running. Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        app.run(port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
