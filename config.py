"""
Configuration file for database and services
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Database Configuration
# Note: DB_PASSWORD bisa kosong jika MySQL tidak menggunakan password
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),  # Kosong jika MySQL tanpa password
    'charset': 'utf8mb4'
}

# Database names for each service
DATABASES = {
    'user_service': os.getenv('DB_NAME_USER', 'educonnect_user'),
    'course_service': os.getenv('DB_NAME_COURSE', 'educonnect_course'),
    'enrollment_service': os.getenv('DB_NAME_ENROLLMENT', 'educonnect_enrollment'),
    'progress_service': os.getenv('DB_NAME_PROGRESS', 'educonnect_progress'),
    'review_service': os.getenv('DB_NAME_REVIEW', 'educonnect_review')
}

# Service URLs
SERVICES = {
    'user': 'http://localhost:5001',
    'course': 'http://localhost:5002',
    'enrollment': 'http://localhost:5003',
    'progress': 'http://localhost:5004',
    'review': 'http://localhost:5005'
}

# API Gateway Configuration
API_GATEWAY_PORT = int(os.getenv('API_GATEWAY_PORT', 5000))
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'educonnect-secret-key-change-in-production')

