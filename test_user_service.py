#!/usr/bin/env python3
"""
Script untuk test User Service secara individual
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("Testing User Service")
print("=" * 60)
print()

try:
    print("1. Testing imports...")
    from services.user_service.app import app, db, User
    print("   ✓ Imports OK")
except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing database connection...")
    with app.app_context():
        db.engine.connect()
        print("   ✓ Database connection OK")
except Exception as e:
    print(f"   ✗ Database connection error: {e}")
    print("\n   Troubleshooting:")
    print("   1. Pastikan MySQL server running")
    print("   2. Cek file .env dan pastikan konfigurasi benar")
    print("   3. Pastikan database sudah dibuat (python setup_database.py)")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing table creation...")
    with app.app_context():
        db.create_all()
        print("   ✓ Tables OK")
except Exception as e:
    print(f"   ✗ Table creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ User Service test passed!")
print("=" * 60)
print("\nService siap dijalankan. Coba jalankan:")
print("  python services/user_service/app.py")

