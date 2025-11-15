#!/usr/bin/env python3
"""
Script untuk test semua services dan menemukan masalah
"""
import subprocess
import sys
import os
from pathlib import Path

SERVICES = [
    {'name': 'API Gateway', 'path': 'api_gateway/app.py'},
    {'name': 'User Service', 'path': 'services/user_service/app.py'},
    {'name': 'Course Service', 'path': 'services/course_service/app.py'},
    {'name': 'Enrollment Service', 'path': 'services/enrollment_service/app.py'},
    {'name': 'Progress Service', 'path': 'services/progress_service/app.py'},
    {'name': 'Review Service', 'path': 'services/review_service/app.py'}
]

def test_service(service_name, service_path):
    """Test if service can be imported and started"""
    print("=" * 70)
    print(f"Testing: {service_name}")
    print("=" * 70)
    
    # Check if file exists
    if not os.path.exists(service_path):
        print(f"[ERROR] File tidak ditemukan: {service_path}")
        return False
    
    print(f"[OK] File ditemukan: {service_path}")
    
    # Check syntax
    print("\n1. Checking syntax...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', service_path],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent
        )
        if result.returncode != 0:
            print(f"[ERROR] Syntax error:")
            print(result.stderr)
            return False
        print("[OK] Syntax OK")
    except Exception as e:
        print(f"[ERROR] Error checking syntax: {e}")
        return False
    
    # Try to import config
    print("\n2. Checking config import...")
    try:
        result = subprocess.run(
            [sys.executable, '-c', 'import sys; sys.path.insert(0, "."); from config import DB_CONFIG, DATABASES; print("Config OK")'],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent
        )
        if result.returncode != 0:
            print(f"[ERROR] Config import error:")
            print(result.stderr)
            if 'ModuleNotFoundError' in result.stderr:
                print("\n  → Pastikan python-dotenv terinstall: pip install python-dotenv")
            return False
        print("[OK] Config import OK")
    except Exception as e:
        print(f"[ERROR] Error importing config: {e}")
        return False
    
    # Check .env file
    print("\n3. Checking .env file...")
    if not os.path.exists('.env'):
        print("[WARNING] File .env tidak ditemukan!")
        print("  → Buat file .env berdasarkan env.example")
        print("  → Minimal isi: DB_HOST, DB_USER, DB_PASSWORD (bisa kosong)")
    else:
        print("[OK] File .env ditemukan")
    
    # Try to run service for 3 seconds to see if it starts
    print("\n4. Testing service startup (3 seconds)...")
    try:
        process = subprocess.Popen(
            [sys.executable, '-u', service_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=Path(__file__).parent
        )
        
        import time
        time.sleep(3)
        
        if process.poll() is not None:
            # Process died
            stdout, _ = process.communicate()
            print(f"[ERROR] Service crashed (exit code: {process.returncode})")
            print("\nError output:")
            if stdout:
                error_lines = stdout.strip().split('\n')
                for line in error_lines[-15:]:
                    if line.strip():
                        print(f"  {line}")
            else:
                print("  (No output captured)")
            return False
        else:
            print("[OK] Service started successfully (still running)")
            process.terminate()
            try:
                process.wait(timeout=2)
            except:
                process.kill()
            return True
            
    except Exception as e:
        print(f"[ERROR] Error starting service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("EduConnect Service Diagnostic Tool")
    print("=" * 70)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    print("-" * 70)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if config.py exists
    if not os.path.exists('config.py'):
        print("[ERROR] config.py tidak ditemukan!")
        return
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("[WARNING] .env tidak ditemukan - beberapa test mungkin gagal")
    
    print()
    
    # Test each service
    results = []
    for service in SERVICES:
        result = test_service(service['name'], service['path'])
        results.append((service['name'], result))
        print()
        time.sleep(0.5)
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"{status}: {name}")
    
    failed = [name for name, result in results if not result]
    if failed:
        print(f"\n[WARNING] {len(failed)} service(s) failed:")
        for name in failed:
            print(f"  - {name}")
        print("\nCek error di atas untuk detail.")
    else:
        print("\n[OK] All services OK!")

if __name__ == '__main__':
    import time
    main()

