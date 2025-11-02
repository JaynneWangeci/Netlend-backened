#!/usr/bin/env python3
"""Simple payment test that bypasses enum issues"""

import requests
import json

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@buyer.com"
TEST_PASSWORD = "testpass123"

def simple_payment_test():
    print("🧪 Simple Payment Test")
    print("=" * 30)
    
    # Login
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test the test-payment endpoint
    print("\n🧪 Testing test-payment endpoint...")
    test_data = {"test": "payment", "amount": 50000}
    response = requests.post(f"{BASE_URL}/api/homebuyer/test-payment", json=test_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test direct payment simulation with known mortgage ID
    print("\n🧪 Testing payment simulation with mortgage ID 10...")
    payment_data = {"mortgage_id": 10, "amount": 25000}
    response = requests.post(f"{BASE_URL}/api/payments/simulate", json=payment_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    simple_payment_test()