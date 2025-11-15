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
db_config['database'] = DATABASES['review_service']

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
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    course_id = db.Column(db.Integer, nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_review'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Routes
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    course_id = request.args.get('course_id')
    user_id = request.args.get('user_id')
    
    query = Review.query
    
    if course_id:
        query = query.filter_by(course_id=course_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    reviews = query.all()
    return jsonify([review.to_dict() for review in reviews]), 200

@app.route('/api/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify(review.to_dict()), 200

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    user_id = data.get('user_id')
    course_id = data.get('course_id')
    rating = data.get('rating')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if review already exists
    existing = Review.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'User has already reviewed this course'}), 400
    
    review = Review(
        user_id=user_id,
        course_id=course_id,
        rating=rating,
        comment=data.get('comment')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict()
    }), 201

@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    data = request.get_json()
    
    if 'rating' in data:
        if data['rating'] < 1 or data['rating'] > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = data['rating']
    
    if 'comment' in data:
        review.comment = data['comment']
    
    review.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict()
    }), 200

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200

@app.route('/api/reviews/course/<int:course_id>/stats', methods=['GET'])
def get_course_review_stats(course_id):
    reviews = Review.query.filter_by(course_id=course_id).all()
    
    if not reviews:
        return jsonify({
            'course_id': course_id,
            'average_rating': 0.0,
            'total_reviews': 0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }), 200
    
    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / len(reviews)
    
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1
    
    return jsonify({
        'course_id': course_id,
        'average_rating': round(average_rating, 2),
        'total_reviews': len(reviews),
        'rating_distribution': rating_distribution
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'review_service'}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Review Service Starting...")
    print("=" * 60)
    
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database initialized")
        except Exception as e:
            print(f"[WARNING] Error initializing database: {e}")
            print("Service will continue running, but database operations may fail.")
    
    print("\nStarting Review Service on port 5005...")
    print("=" * 60)
    try:
        app.run(port=5005, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
