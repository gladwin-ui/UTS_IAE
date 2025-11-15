"""
API Gateway untuk EduConnect
Menerima semua request dari frontend dan meneruskan ke service terkait
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import os
import sys
from functools import wraps

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SERVICES, JWT_SECRET_KEY

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
CORS(app)

# Service URLs
USER_SERVICE = SERVICES['user']
COURSE_SERVICE = SERVICES['course']
ENROLLMENT_SERVICE = SERVICES['enrollment']
PROGRESS_SERVICE = SERVICES['progress']
REVIEW_SERVICE = SERVICES['review']

def forward_request(service_url, path, method='GET', data=None, headers=None):
    """Forward request ke service terkait"""
    try:
        url = f"{service_url}{path}"
        request_headers = {'Content-Type': 'application/json'}
        
        # Forward authorization header jika ada
        if headers and 'Authorization' in headers:
            request_headers['Authorization'] = headers['Authorization']
        
        # Forward request berdasarkan method
        if method == 'GET':
            response = requests.get(url, params=request.args, headers=request_headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=request_headers, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=request_headers, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=request_headers, timeout=30)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        # Return response dengan status code yang sama
        try:
            if response.content:
                # Try to parse as JSON
                try:
                    response_data = response.json()
                except ValueError:
                    # If not JSON, return error
                    return jsonify({
                        'error': 'Invalid response from service',
                        'message': f'Service {service_url} returned non-JSON response',
                        'status_code': response.status_code,
                        'raw_response': response.text[:500]
                    }), 502
            else:
                response_data = {}
            
            return make_response(
                response_data,
                response.status_code
            )
        except Exception as e:
            return jsonify({
                'error': 'Error processing service response',
                'message': str(e),
                'service': service_url
            }), 502
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': f'Service unavailable: {service_url}',
            'message': 'Pastikan service sedang running. Cek: python run_services.py'
        }), 503
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'message': f'Service {service_url} tidak merespon dalam 30 detik. Pastikan service running dan database terhubung.'
        }), 504
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'message': 'Internal gateway error'
        }), 500

# ==================== USER SERVICE ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register user baru"""
    return forward_request(USER_SERVICE, '/api/register', 'POST', request.get_json(), request.headers)

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    return forward_request(USER_SERVICE, '/api/login', 'POST', request.get_json(), request.headers)

@app.route('/api/users/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    return forward_request(USER_SERVICE, '/api/users/me', 'GET', None, request.headers)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    return forward_request(USER_SERVICE, f'/api/users/{user_id}', 'GET', None, request.headers)

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return forward_request(USER_SERVICE, '/api/users', 'GET', None, request.headers)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    return forward_request(USER_SERVICE, f'/api/users/{user_id}', 'PUT', request.get_json(), request.headers)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    return forward_request(USER_SERVICE, f'/api/users/{user_id}', 'DELETE', None, request.headers)

# ==================== COURSE SERVICE ROUTES ====================

@app.route('/api/courses', methods=['GET', 'POST'])
def courses():
    """Get all courses or create new course"""
    if request.method == 'GET':
        return forward_request(COURSE_SERVICE, '/api/courses', 'GET', None, request.headers)
    else:
        return forward_request(COURSE_SERVICE, '/api/courses', 'POST', request.get_json(), request.headers)

@app.route('/api/courses/<int:course_id>', methods=['GET', 'PUT', 'DELETE'])
def course_detail(course_id):
    """Get, update, or delete course"""
    if request.method == 'GET':
        return forward_request(COURSE_SERVICE, f'/api/courses/{course_id}', 'GET', None, request.headers)
    elif request.method == 'PUT':
        return forward_request(COURSE_SERVICE, f'/api/courses/{course_id}', 'PUT', request.get_json(), request.headers)
    else:
        return forward_request(COURSE_SERVICE, f'/api/courses/{course_id}', 'DELETE', None, request.headers)

# ==================== ENROLLMENT SERVICE ROUTES ====================

@app.route('/api/enrollments', methods=['GET', 'POST'])
def enrollments():
    """Get all enrollments or create new enrollment"""
    if request.method == 'GET':
        return forward_request(ENROLLMENT_SERVICE, '/api/enrollments', 'GET', None, request.headers)
    else:
        return forward_request(ENROLLMENT_SERVICE, '/api/enrollments', 'POST', request.get_json(), request.headers)

@app.route('/api/enrollments/<int:enrollment_id>', methods=['GET', 'PUT', 'DELETE'])
def enrollment_detail(enrollment_id):
    """Get, update, or delete enrollment"""
    if request.method == 'GET':
        return forward_request(ENROLLMENT_SERVICE, f'/api/enrollments/{enrollment_id}', 'GET', None, request.headers)
    elif request.method == 'PUT':
        return forward_request(ENROLLMENT_SERVICE, f'/api/enrollments/{enrollment_id}', 'PUT', request.get_json(), request.headers)
    else:
        return forward_request(ENROLLMENT_SERVICE, f'/api/enrollments/{enrollment_id}', 'DELETE', None, request.headers)

@app.route('/api/enrollments/user/<int:user_id>/courses', methods=['GET'])
def user_enrolled_courses(user_id):
    """Get courses enrolled by user"""
    return forward_request(ENROLLMENT_SERVICE, f'/api/enrollments/user/{user_id}/courses', 'GET', None, request.headers)

# ==================== PROGRESS SERVICE ROUTES ====================

@app.route('/api/progress', methods=['GET', 'POST'])
def progress():
    """Get all progress or create new progress"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, '/api/progress', 'GET', None, request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, '/api/progress', 'POST', request.get_json(), request.headers)

@app.route('/api/progress/<int:progress_id>', methods=['GET', 'PUT'])
def progress_detail(progress_id):
    """Get or update progress"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, f'/api/progress/{progress_id}', 'GET', None, request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, f'/api/progress/{progress_id}', 'PUT', request.get_json(), request.headers)

@app.route('/api/progress/user/<int:user_id>/course/<int:course_id>', methods=['GET'])
def user_course_progress(user_id, course_id):
    """Get user progress for specific course"""
    return forward_request(PROGRESS_SERVICE, f'/api/progress/user/{user_id}/course/{course_id}', 'GET', None, request.headers)

# ==================== MODULE ROUTES ====================

@app.route('/api/modules', methods=['GET'])
def modules():
    """Get all modules for a course"""
    return forward_request(PROGRESS_SERVICE, '/api/modules', 'GET', None, request.headers)

@app.route('/api/modules/<int:module_id>', methods=['GET'])
def module_detail(module_id):
    """Get module by ID"""
    return forward_request(PROGRESS_SERVICE, f'/api/modules/{module_id}', 'GET', None, request.headers)

# ==================== TASK ROUTES ====================

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    """Get all tasks or create new task"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, '/api/tasks', 'GET', None, request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, '/api/tasks', 'POST', request.get_json(), request.headers)

@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    """Get, update, or delete task"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, f'/api/tasks/{task_id}', 'GET', None, request.headers)
    elif request.method == 'PUT':
        return forward_request(PROGRESS_SERVICE, f'/api/tasks/{task_id}', 'PUT', request.get_json(), request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, f'/api/tasks/{task_id}', 'DELETE', None, request.headers)

@app.route('/api/tasks/user/<int:user_id>/course/<int:course_id>', methods=['GET'])
def user_course_tasks(user_id, course_id):
    """Get tasks for user in specific course"""
    return forward_request(PROGRESS_SERVICE, f'/api/tasks/user/{user_id}/course/{course_id}', 'GET', None, request.headers)

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark task as completed by user"""
    return forward_request(PROGRESS_SERVICE, f'/api/tasks/{task_id}/complete', 'POST', request.get_json(), request.headers)

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update user task status"""
    return forward_request(PROGRESS_SERVICE, f'/api/tasks/{task_id}/status', 'PUT', request.get_json(), request.headers)

@app.route('/api/tasks/initialize', methods=['POST'])
def initialize_tasks():
    """Initialize sample tasks for courses"""
    return forward_request(PROGRESS_SERVICE, '/api/tasks/initialize', 'POST', None, request.headers)

# ==================== SUBMISSION ROUTES ====================

@app.route('/api/submissions', methods=['GET', 'POST'])
def submissions():
    """Get all submissions or create new submission"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, '/api/submissions', 'GET', None, request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, '/api/submissions', 'POST', request.get_json(), request.headers)

@app.route('/api/submissions/<int:submission_id>', methods=['GET', 'PUT'])
def submission_detail(submission_id):
    """Get or update submission"""
    if request.method == 'GET':
        return forward_request(PROGRESS_SERVICE, f'/api/submissions/{submission_id}', 'GET', None, request.headers)
    else:
        return forward_request(PROGRESS_SERVICE, f'/api/submissions/{submission_id}', 'PUT', request.get_json(), request.headers)

@app.route('/api/submissions/user/<int:user_id>/task/<int:task_id>', methods=['GET'])
def user_task_submission(user_id, task_id):
    """Get user's submission for a specific task"""
    return forward_request(PROGRESS_SERVICE, f'/api/submissions/user/{user_id}/task/{task_id}', 'GET', None, request.headers)

# ==================== REVIEW SERVICE ROUTES ====================

@app.route('/api/reviews', methods=['GET', 'POST'])
def reviews():
    """Get all reviews or create new review"""
    if request.method == 'GET':
        return forward_request(REVIEW_SERVICE, '/api/reviews', 'GET', None, request.headers)
    else:
        return forward_request(REVIEW_SERVICE, '/api/reviews', 'POST', request.get_json(), request.headers)

@app.route('/api/reviews/<int:review_id>', methods=['GET', 'PUT', 'DELETE'])
def review_detail(review_id):
    """Get, update, or delete review"""
    if request.method == 'GET':
        return forward_request(REVIEW_SERVICE, f'/api/reviews/{review_id}', 'GET', None, request.headers)
    elif request.method == 'PUT':
        return forward_request(REVIEW_SERVICE, f'/api/reviews/{review_id}', 'PUT', request.get_json(), request.headers)
    else:
        return forward_request(REVIEW_SERVICE, f'/api/reviews/{review_id}', 'DELETE', None, request.headers)

@app.route('/api/reviews/course/<int:course_id>/stats', methods=['GET'])
def course_review_stats(course_id):
    """Get review statistics for course"""
    return forward_request(REVIEW_SERVICE, f'/api/reviews/course/{course_id}/stats', 'GET', None, request.headers)

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check untuk API Gateway"""
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/api/health", timeout=2)
            services_status[service_name] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            services_status[service_name] = 'unavailable'
    
    return jsonify({
        'status': 'healthy',
        'gateway': 'running',
        'services': services_status
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API Gateway info"""
    return jsonify({
        'message': 'EduConnect API Gateway',
        'version': '1.0.0',
        'note': 'This is the API Gateway. Frontend should be accessed at http://localhost:8000',
        'endpoints': {
            'auth': '/api/auth/login, /api/auth/register',
            'users': '/api/users',
            'courses': '/api/courses',
            'enrollments': '/api/enrollments',
            'progress': '/api/progress',
            'reviews': '/api/reviews'
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'This is the API Gateway. Please access the frontend at http://localhost:8000',
        'available_endpoints': {
            'auth': '/api/auth/login, /api/auth/register',
            'users': '/api/users',
            'courses': '/api/courses',
            'enrollments': '/api/enrollments',
            'progress': '/api/progress',
            'reviews': '/api/reviews'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An error occurred in the API Gateway'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("API Gateway Starting...")
    print("=" * 60)
    print(f"Services:")
    for name, url in SERVICES.items():
        print(f"  - {name}: {url}")
    print("\nStarting API Gateway on port 5000...")
    print("=" * 60)
    try:
        app.run(port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] Service error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

