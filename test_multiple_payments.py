#!/usr/bin/env python3
"""Test multiple payments to verify consistency"""

import requests
import json

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@buyer.com"
TEST_PASSWORD = "testpass123"

def test_multiple_payments():
    print("🧪 Testing Multiple Payments")
    print("=" * 40)
    
    # Login
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test 3 payments
    payments = [
        {"mortgage_id": 10, "amount": 30000},
        {"mortgage_id": 10, "amount": 45000},
        {"mortgage_id": 10, "amount": 20000}
    ]
    
    for i, payment_data in enumerate(payments, 1):
        print(f"\n💰 Payment {i}: KES {payment_data['amount']:,}")
        response = requests.post(f"{BASE_URL}/api/payments/simulate", json=payment_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            remaining_balance = result['modal']['details']['remaining_balance']
            print(f"✅ Success! Remaining balance: KES {remaining_balance:,.2f}")
        else:
            print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_multiple_payments()