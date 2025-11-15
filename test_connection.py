#!/usr/bin/env python3
"""
Script untuk test koneksi ke semua services
"""
import requests
import sys

SERVICES = {
    'API Gateway': 'http://localhost:5000',
    'User Service': 'http://localhost:5001',
    'Course Service': 'http://localhost:5002',
    'Enrollment Service': 'http://localhost:5003',
    'Progress Service': 'http://localhost:5004',
    'Review Service': 'http://localhost:5005'
}

def test_service(name, url):
    """Test if service is accessible"""
    try:
        response = requests.get(f"{url}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ {name} - OK")
            return True
        else:
            print(f"✗ {name} - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ {name} - Connection refused (Service tidak running)")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ {name} - Timeout (Service tidak merespon)")
        return False
    except Exception as e:
        print(f"✗ {name} - Error: {e}")
        return False

def test_api_gateway_routing():
    """Test API Gateway routing"""
    print("\n" + "=" * 60)
    print("Testing API Gateway Routing")
    print("=" * 60)
    
    # Test register endpoint
    try:
        import time
        test_data = {
            'username': 'test_user_' + str(int(time.time())),
            'email': f'test_{int(time.time())}@test.com',
            'password': 'test123',
            'full_name': 'Test User'
        }
        
        print(f"\nTesting POST /api/auth/register...")
        print(f"Test data: username={test_data['username']}")
        
        response = requests.post(
            'http://localhost:5000/api/auth/register',
            json=test_data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        # Try to parse response
        try:
            response_data = response.json()
            print(f"Response Data: {response_data}")
        except:
            print(f"⚠ Response is not JSON!")
            print(f"Raw Response (first 500 chars): {response.text[:500]}")
            return False
        
        if response.status_code in [201, 400]:  # 201 = success, 400 = user exists
            print(f"✓ API Gateway routing OK (Status: {response.status_code})")
            if response.status_code == 201:
                print("  ✓ User registered successfully")
            else:
                print("  ℹ User already exists (expected if test run before)")
            return True
        elif response.status_code == 503:
            print(f"✗ Service unavailable")
            print(f"  Error: {response_data.get('error', 'Unknown')}")
            print(f"  Message: {response_data.get('message', 'No message')}")
            return False
        elif response.status_code == 502:
            print(f"✗ Bad Gateway - Service returned invalid response")
            print(f"  Error: {response_data.get('error', 'Unknown')}")
            print(f"  Message: {response_data.get('message', 'No message')}")
            return False
        else:
            print(f"✗ API Gateway routing error (Status: {response.status_code})")
            print(f"  Response: {response_data}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ API Gateway tidak bisa diakses")
        print("  Pastikan API Gateway running di port 5000")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timeout - User Service mungkin tidak running atau database error")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("EduConnect Connection Test")
    print("=" * 60)
    print()
    
    # Test all services
    print("Testing Services Health:")
    print("-" * 60)
    results = []
    for name, url in SERVICES.items():
        results.append(test_service(name, url))
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(results):
        print("✓ All services are running!")
    else:
        print("✗ Some services are not running!")
        print("\nSolutions:")
        print("1. Pastikan semua services running: python run_services.py")
        print("2. Cek apakah port 5000-5005 tidak digunakan aplikasi lain")
        print("3. Restart services jika perlu")
    
    # Test API Gateway routing
    if results[0]:  # If API Gateway is running
        test_api_gateway_routing()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        sys.exit(0)

