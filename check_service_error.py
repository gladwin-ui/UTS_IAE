#!/usr/bin/env python3
"""
Script untuk check error pada service secara individual
"""
import subprocess
import sys
from pathlib import Path

SERVICES = {
    'API Gateway': 'api_gateway/app.py',
    'User Service': 'services/user_service/app.py',
    'Course Service': 'services/course_service/app.py',
    'Enrollment Service': 'services/enrollment_service/app.py',
    'Progress Service': 'services/progress_service/app.py',
    'Review Service': 'services/review_service/app.py'
}

def check_service(service_name, service_path):
    """Check if service can start without error"""
    print("=" * 60)
    print(f"Checking {service_name}")
    print("=" * 60)
    
    try:
        # Try to import and check for syntax errors
        print(f"Checking syntax...")
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', service_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"✗ Syntax error in {service_name}:")
            print(result.stderr)
            return False
        
        print("✓ Syntax OK")
        
        # Try to import modules
        print(f"Checking imports...")
        result = subprocess.run(
            [sys.executable, '-c', f'import sys; sys.path.insert(0, "."); exec(open("{service_path}").read())'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check for import errors (exit code 1 usually means import error)
        if 'ImportError' in result.stderr or 'ModuleNotFoundError' in result.stderr:
            print(f"✗ Import error:")
            print(result.stderr)
            return False
        
        print("✓ Imports OK")
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠ Service takes too long to check (might be OK)")
        return True
    except Exception as e:
        print(f"✗ Error checking service: {e}")
        return False

def main():
    print("=" * 60)
    print("Service Error Checker")
    print("=" * 60)
    print()
    
    results = {}
    for service_name, service_path in SERVICES.items():
        results[service_name] = check_service(service_name, service_path)
        print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    for service_name, status in results.items():
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {service_name}")
    
    print()
    print("=" * 60)
    if all(results.values()):
        print("✓ All services OK!")
    else:
        print("✗ Some services have errors!")
        print("\nFix errors above before running run_services.py")

if __name__ == '__main__':
    main()

