#!/usr/bin/env python3
"""
Main orchestrator script to run all microservices
Improved version with better error handling and monitoring
"""
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path
from queue import Queue

# Service configurations
SERVICES = [
    {
        'name': 'API Gateway',
        'port': 5000,
        'path': 'api_gateway/app.py',
        'process': None,
        'output_queue': None
    },
    {
        'name': 'User Service',
        'port': 5001,
        'path': 'services/user_service/app.py',
        'process': None,
        'output_queue': None
    },
    {
        'name': 'Course Service',
        'port': 5002,
        'path': 'services/course_service/app.py',
        'process': None,
        'output_queue': None
    },
    {
        'name': 'Enrollment Service',
        'port': 5003,
        'path': 'services/enrollment_service/app.py',
        'process': None,
        'output_queue': None
    },
    {
        'name': 'Progress Service',
        'port': 5004,
        'path': 'services/progress_service/app.py',
        'process': None,
        'output_queue': None
    },
    {
        'name': 'Review Service',
        'port': 5005,
        'path': 'services/review_service/app.py',
        'process': None,
        'output_queue': None
    }
]

processes = []
running = True

def read_output(pipe, queue, service_name):
    """Read output from service process"""
    try:
        for line in iter(pipe.readline, ''):
            if not running:
                break
            if line:
                queue.put((service_name, line.strip()))
        pipe.close()
    except:
        pass

def start_service(service):
    """Start a single service"""
    print(f"Starting {service['name']} on port {service['port']}...")
    try:
        # Create output queue for this service
        service['output_queue'] = Queue()
        
        # Start process with unbuffered output
        process = subprocess.Popen(
            [sys.executable, '-u', service['path']],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=Path(__file__).parent,
            text=True,
            bufsize=1
        )
        
        service['process'] = process
        processes.append(process)
        
        # Start thread to read output
        output_thread = threading.Thread(
            target=read_output,
            args=(process.stdout, service['output_queue'], service['name']),
            daemon=True
        )
        output_thread.start()
        
        # Wait a bit to check if process crashes immediately
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process died, collect error output
            error_lines = []
            try:
                while not service['output_queue'].empty():
                    _, line = service['output_queue'].get_nowait()
                    error_lines.append(line)
            except:
                pass
            
            print(f"\n[ERROR] {service['name']} failed to start!")
            print(f"  Exit code: {process.returncode}")
            
            if error_lines:
                print(f"  Error output (last 20 lines):")
                for line in error_lines[-20:]:
                    if line.strip():
                        print(f"    {line}")
            else:
                print(f"  (No error output captured)")
            
            print(f"\n  Troubleshooting untuk {service['name']}:")
            if 'user' in service['name'].lower():
                print("    - Pastikan MySQL running")
                print("    - Cek file .env (DB_PASSWORD bisa kosong jika MySQL tanpa password)")
                print("    - Pastikan database educonnect_user sudah dibuat")
                print("    - Test dengan: python services/user_service/app.py")
            else:
                print("    - Pastikan MySQL running")
                print("    - Cek file .env")
                print("    - Pastikan database sudah dibuat")
            
            return False
        
        print(f"[OK] {service['name']} started (PID: {process.pid})")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to start {service['name']}: {e}")
        import traceback
        traceback.print_exc()
        return False

def stop_services():
    """Stop all running services"""
    global running
    running = False
    
    print("\n" + "=" * 60)
    print("Stopping all services...")
    print("=" * 60)
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"[OK] Stopped process {process.pid}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"[OK] Killed process {process.pid}")
            except Exception as e:
                print(f"[ERROR] Error stopping process: {e}")

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\n\nReceived interrupt signal")
    stop_services()
    sys.exit(0)

def monitor_services():
    """Monitor services and print their output"""
    while running:
        for service in SERVICES:
            if service['output_queue']:
                try:
                    while not service['output_queue'].empty():
                        service_name, line = service['output_queue'].get_nowait()
                        # Only print important messages
                        if any(keyword in line.lower() for keyword in ['error', 'warning', 'failed', 'exception', 'traceback']):
                            print(f"[{service_name}] {line}")
                except:
                    pass
        time.sleep(0.5)

def main():
    """Main function to start all services"""
    global running
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("EduConnect Microservices Orchestrator")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    if not os.path.exists('.env'):
        print("[WARNING] File .env tidak ditemukan!")
        print("   Pastikan file .env sudah dibuat sebelum menjalankan services.")
        print()
    
    # Start all services
    print("Starting services...")
    print("-" * 60)
    failed_services = []
    
    for service in SERVICES:
        if not start_service(service):
            failed_services.append(service['name'])
        time.sleep(1)  # Small delay between service starts
    
    if failed_services:
        print("\n" + "=" * 60)
        print("[WARNING] Some services failed to start!")
        print("=" * 60)
        print("Failed services:")
        for name in failed_services:
            print(f"  [ERROR] {name}")
        print("\nServices yang berhasil start akan tetap running.")
        print("Fix errors di atas dan restart service yang gagal.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[OK] All services started successfully!")
        print("=" * 60)
    
    print("\nServices:")
    for service in SERVICES:
        if service['process'] and service['process'].poll() is None:
            print(f"  [OK] {service['name']}: http://localhost:{service['port']}")
        else:
            print(f"  [ERROR] {service['name']}: FAILED")
    
    print("\nAPI Gateway: http://localhost:5000")
    print("\nFrontend:")
    print("  Run 'python serve_frontend.py' in a separate terminal")
    print("  Or open http://localhost:8000 after starting the frontend server")
    print("\nNote: Frontend now connects only to API Gateway (port 5000)")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 60)
    print()
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_services, daemon=True)
    monitor_thread.start()
    
    # Keep the script running and monitor services
    try:
        while running:
            # Check if any process has died
            for service in SERVICES:
                if service['process'] and service['process'].poll() is not None:
                    exit_code = service['process'].returncode
                    print(f"\n" + "=" * 60)
                    print(f"[ERROR] {service['name']} has stopped unexpectedly!")
                    print("=" * 60)
                    print(f"Exit code: {exit_code}")
                    
                    # Collect error output
                    error_lines = []
                    if service['output_queue']:
                        try:
                            while not service['output_queue'].empty():
                                _, line = service['output_queue'].get_nowait()
                                error_lines.append(line)
                        except:
                            pass
                    
                    if error_lines:
                        print("\nError output (last 30 lines):")
                        for line in error_lines[-30:]:
                            if line.strip():
                                print(f"  {line}")
                    
                    print("\n" + "=" * 60)
                    print("Troubleshooting:")
                    print("1. Cek error di atas untuk detail")
                    print("2. Pastikan MySQL running dan database sudah dibuat")
                    print("3. Cek file .env dan pastikan konfigurasi benar")
                    print("4. Cek apakah port sudah digunakan aplikasi lain")
                    print("5. Test service individual: python " + service['path'])
                    print("=" * 60)
                    print("\nOther services will continue running.")
                    print("Fix the error and restart this script to restart the failed service.")
                    print()
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()
