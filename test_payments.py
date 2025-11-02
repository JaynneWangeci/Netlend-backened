#!/usr/bin/env python3
"""
Test script for payment simulation functionality
"""

from app import create_app, db
from models import *
from datetime import datetime, timedelta

def test_payment_simulation():
    app = create_app()
    
    with app.app_context():
        # Create test data if not exists
        
        # Create a test lender
        lender = Lender.query.first()
        if not lender:
            lender = Lender(
                institution_name="Test Bank",
                contact_person="Test Contact",
                email="test@bank.com",
                verified=True
            )
            lender.set_password("password")
            db.session.add(lender)
        
        # Create a test buyer
        buyer = Buyer.query.first()
        if not buyer:
            buyer = Buyer(
                name="Test Buyer",
                email="buyer@test.com",
                verified=True,
                monthly_net_income=100000,
                estimated_property_value=5000000,
                desired_loan_amount=4000000
            )
            buyer.set_password("password")
            db.session.add(buyer)
        
        # Create a test listing
        listing = MortgageListing.query.first()
        if not listing:
            listing = MortgageListing(
                lender_id=lender.id,
                property_title="Test Property",
                property_type=PropertyType.APARTMENT,
                bedrooms=3,
                address="Test Address",
                county=KenyanCounty.NAIROBI,
                price_range=5000000,
                interest_rate=12.0,
                repayment_period=25,
                down_payment=1000000,
                monthly_payment=45000,
                status=ListingStatus.ACTIVE
            )
            db.session.add(listing)
        
        # Create a test application
        application = MortgageApplication.query.first()
        if not application:
            application = MortgageApplication(
                borrower_id=buyer.id,
                lender_id=lender.id,
                listing_id=listing.id,
                requested_amount=4000000,
                repayment_years=25,
                status=ApplicationStatus.APPROVED
            )
            db.session.add(application)
        
        # Create an active mortgage
        mortgage = ActiveMortgage.query.first()
        if not mortgage:
            mortgage = ActiveMortgage(
                application_id=application.id,
                borrower_id=buyer.id,
                lender_id=lender.id,
                principal_amount=4000000,
                interest_rate=12.0,
                repayment_term=300,  # 25 years * 12 months
                remaining_balance=4000000,
                next_payment_due=datetime.now().date() + timedelta(days=30)
            )
            db.session.add(mortgage)
        
        db.session.commit()
        
        print("✅ Test data created successfully!")
        print(f"Lender ID: {lender.id}")
        print(f"Buyer ID: {buyer.id}")
        print(f"Mortgage ID: {mortgage.id}")
        print(f"Listing ID: {listing.id}")
        
        # Test payment simulation
        payment = PaymentSchedule(
            mortgage_id=mortgage.id,
            payment_date=datetime.now().date(),
            amount_due=45000,
            amount_paid=45000,
            status=PaymentStatus.PAID,
            receipt_url="test_receipt.pdf"
        )
        
        # Update mortgage balance
        mortgage.remaining_balance -= 45000
        
        db.session.add(payment)
        db.session.commit()
        
        print("✅ Test payment created successfully!")
        print(f"Payment ID: {payment.id}")
        print(f"Remaining Balance: {mortgage.remaining_balance}")

if __name__ == "__main__":
    test_payment_simulation()