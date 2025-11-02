#!/usr/bin/env python3
"""Test script to verify payment processing endpoints are working"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@buyer.com"
TEST_PASSWORD = "testpass123"

def test_payment_endpoints():
    print("🧪 Testing NetLend Payment Endpoints")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("token")
            user_info = response.json().get("user")
            print(f"✅ Login successful: {user_info['name']} ({user_info['userType']})")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get mortgages
    print("\n2. Getting mortgages...")
    try:
        response = requests.get(f"{BASE_URL}/api/homebuyer/my-mortgages", headers=headers)
        if response.status_code == 200:
            mortgages = response.json()
            print(f"✅ Found {len(mortgages)} mortgages")
            if mortgages:
                mortgage = mortgages[0]
                print(f"   First mortgage: ID {mortgage['id']}, Balance: {mortgage['remainingBalance']}")
                mortgage_id = mortgage['id']
            else:
                print("❌ No mortgages found")
                return
        else:
            print(f"❌ Failed to get mortgages: {response.text}")
            return
    except Exception as e:
        print(f"❌ Mortgage fetch error: {e}")
        return
    
    # Step 3: Test payment simulation
    print("\n3. Testing payment simulation...")
    # Use the latest mortgage (ID 10)
    if len(mortgages) > 1:
        mortgage_id = mortgages[-1]['id']  # Use the last (newest) mortgage
        print(f"Using mortgage ID: {mortgage_id}")
    
    payment_data = {
        "mortgage_id": mortgage_id,
        "amount": 50000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/payments/simulate", json=payment_data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment simulation successful!")
            if result.get('modal'):
                print(f"   Message: {result['modal']['message']}")
        else:
            print(f"❌ Payment simulation failed: {response.text}")
    except Exception as e:
        print(f"❌ Payment simulation error: {e}")
    
    # Step 4: Check updated mortgage balance
    print("\n4. Checking updated mortgage balance...")
    try:
        response = requests.get(f"{BASE_URL}/api/homebuyer/my-mortgages", headers=headers)
        if response.status_code == 200:
            mortgages = response.json()
            updated_mortgage = next((m for m in mortgages if m['id'] == mortgage_id), None)
            if updated_mortgage:
                print(f"✅ Updated balance: {updated_mortgage['remainingBalance']}")
            else:
                print("❌ Mortgage not found in updated list")
        else:
            print(f"❌ Failed to get updated mortgages: {response.text}")
    except Exception as e:
        print(f"❌ Updated mortgage fetch error: {e}")

if __name__ == "__main__":
    test_payment_endpoints()