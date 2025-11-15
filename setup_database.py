#!/usr/bin/env python3
"""
Script Python untuk setup database MySQL
Alternatif jika command mysql tidak bisa dijalankan
"""
import pymysql
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Database names
DATABASES = [
    'educonnect_user',
    'educonnect_course',
    'educonnect_enrollment',
    'educonnect_progress',
    'educonnect_review'
]

def create_databases():
    """Create all required databases"""
    try:
        # Connect to MySQL server (without specifying database)
        print("Connecting to MySQL server...")
        # Handle empty password
        connect_kwargs = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'charset': 'utf8mb4'
        }
        if DB_PASSWORD:
            connect_kwargs['password'] = DB_PASSWORD
        
        connection = pymysql.connect(**connect_kwargs)
        
        print("✓ Connected to MySQL server")
        
        with connection.cursor() as cursor:
            # Create each database
            for db_name in DATABASES:
                try:
                    # Create database if not exists
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"✓ Database '{db_name}' created/verified")
                except Exception as e:
                    print(f"✗ Error creating database '{db_name}': {e}")
                    return False
            
            # Show created databases
            cursor.execute("SHOW DATABASES LIKE 'educonnect_%'")
            databases = cursor.fetchall()
            
            print("\n" + "=" * 60)
            print("Databases created successfully:")
            print("=" * 60)
            for db in databases:
                print(f"  • {db[0]}")
            print("=" * 60)
            
        connection.commit()
        connection.close()
        print("\n✓ All databases setup completed!")
        return True
        
    except pymysql.Error as e:
        print(f"\n✗ MySQL Error: {e}")
        print("\nTroubleshooting:")
        print("1. Pastikan MySQL server sedang running")
        print("2. Cek username dan password di file .env")
        print("   (Jika MySQL tanpa password, biarkan DB_PASSWORD kosong)")
        print("3. Pastikan user memiliki privilege untuk membuat database")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("EduConnect Database Setup")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  File .env tidak ditemukan!")
        print("\nLangkah-langkah:")
        print("1. Copy env.example ke .env:")
        print("   copy env.example .env  # Windows")
        print("   cp env.example .env    # Linux/Mac")
        print("2. Edit file .env")
        print("   - Jika MySQL pakai password: isi DB_PASSWORD=password_anda")
        print("   - Jika MySQL tanpa password: biarkan DB_PASSWORD kosong atau hapus barisnya")
        print("3. Simpan file dan jalankan script ini lagi")
        return
    
    # Check if password is set (kosong juga OK jika MySQL tidak pakai password)
    print(f"MySQL Configuration:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  User: {DB_USER}")
    if DB_PASSWORD:
        print(f"  Password: {'*' * len(DB_PASSWORD)}")
    else:
        print(f"  Password: (kosong - MySQL tanpa password)")
    print()
    
    # Ask for confirmation
    response = input("Lanjutkan setup database? (y/n): ")
    if response.lower() != 'y':
        print("Setup dibatalkan.")
        return
    
    print()
    
    # Create databases
    if create_databases():
        print("\n✅ Setup database berhasil!")
        print("\nSelanjutnya:")
        print("1. Jalankan: python run_services.py")
        print("2. Services akan otomatis membuat tabel di database")
    else:
        print("\n❌ Setup database gagal!")
        print("\nCoba cara alternatif:")
        print("1. Buka MySQL Workbench atau MySQL client")
        print("2. Copy-paste isi file setup_database.sql")
        print("3. Jalankan query tersebut")

if __name__ == '__main__':
    main()

