from app import create_app, db
from models import Lender, MortgageListing, PropertyType, KenyanCounty, ListingStatus, Buyer, MortgageApplication, ApplicationStatus
from werkzeug.security import generate_password_hash

def seed_lenders():
    app = create_app()
    with app.app_context():
        # Create mock lenders
        lenders = [
            {
                'institution_name': 'Kenya Commercial Bank',
                'contact_person': 'John Mwangi',
                'email': 'john@kcb.co.ke',
                'password': 'password123',
                'phone_number': '+254700123456',
                'business_registration_number': 'KCB001',
                'verified': True
            },
            {
                'institution_name': 'Equity Bank',
                'contact_person': 'Mary Wanjiku',
                'email': 'mary@equitybank.co.ke',
                'password': 'password123',
                'phone_number': '+254700234567',
                'business_registration_number': 'EQB002',
                'verified': True
            },
            {
                'institution_name': 'Cooperative Bank',
                'contact_person': 'Peter Kiprotich',
                'email': 'peter@coop.co.ke',
                'password': 'password123',
                'phone_number': '+254700345678',
                'business_registration_number': 'COOP003',
                'verified': True
            }
        ]
        
        for lender_data in lenders:
            existing = Lender.query.filter_by(email=lender_data['email']).first()
            if not existing:
                lender = Lender(
                    institution_name=lender_data['institution_name'],
                    contact_person=lender_data['contact_person'],
                    email=lender_data['email'],
                    phone_number=lender_data['phone_number'],
                    business_registration_number=lender_data['business_registration_number'],
                    verified=lender_data['verified']
                )
                lender.set_password(lender_data['password'])
                db.session.add(lender)
        
        db.session.commit()
        print("Lenders created successfully!")
        
        # Create mock mortgage listings
        listings = [
            {
                'lender_id': 1,
                'property_title': 'Modern 3BR Apartment in Westlands',
                'property_type': PropertyType.APARTMENT,
                'bedrooms': 3,
                'address': '123 Westlands Road',
                'county': KenyanCounty.NAIROBI,
                'price_range': 8500000,
                'interest_rate': 12.5,
                'repayment_period': 20,
                'down_payment': 1700000,
                'eligibility_criteria': 'Minimum income KSH 150,000/month',
                'images': [
                    'https://res.cloudinary.com/demo/image/upload/sample.jpg',
                    'https://res.cloudinary.com/demo/image/upload/sample2.jpg'
                ]
            },
            {
                'lender_id': 2,
                'property_title': '4BR Villa in Karen',
                'property_type': PropertyType.VILLA,
                'bedrooms': 4,
                'address': '456 Karen Road',
                'county': KenyanCounty.NAIROBI,
                'price_range': 15000000,
                'interest_rate': 11.8,
                'repayment_period': 25,
                'down_payment': 3000000,
                'eligibility_criteria': 'Minimum income KSH 250,000/month',
                'images': [
                    'https://res.cloudinary.com/demo/image/upload/sample3.jpg',
                    'https://res.cloudinary.com/demo/image/upload/sample4.jpg'
                ]
            },
            {
                'lender_id': 3,
                'property_title': '2BR Townhouse in Kiambu',
                'property_type': PropertyType.TOWNHOUSE,
                'bedrooms': 2,
                'address': '789 Kiambu Town',
                'county': KenyanCounty.KIAMBU,
                'price_range': 5500000,
                'interest_rate': 13.2,
                'repayment_period': 15,
                'down_payment': 1100000,
                'eligibility_criteria': 'Minimum income KSH 100,000/month',
                'images': [
                    'https://res.cloudinary.com/demo/image/upload/sample5.jpg'
                ]
            }
        ]
        
        for listing_data in listings:
            listing = MortgageListing(**listing_data)
            db.session.add(listing)
        
        db.session.commit()
        print("Mock mortgage listings created successfully!")
        
        # Create mock buyers
        buyers = [
            {
                'name': 'Sarah Wanjiku',
                'email': 'sarah@gmail.com',
                'password': 'password123',
                'phone_number': '+254701234567'
            },
            {
                'name': 'David Kimani',
                'email': 'david@gmail.com', 
                'password': 'password123',
                'phone_number': '+254702345678'
            },
            {
                'name': 'Grace Achieng',
                'email': 'grace@gmail.com',
                'password': 'password123',
                'phone_number': '+254703456789'
            }
        ]
        
        for buyer_data in buyers:
            existing = Buyer.query.filter_by(email=buyer_data['email']).first()
            if not existing:
                buyer = Buyer(
                    name=buyer_data['name'],
                    email=buyer_data['email'],
                    phone_number=buyer_data['phone_number'],
                    verified=True
                )
                buyer.set_password(buyer_data['password'])
                db.session.add(buyer)
        
        db.session.commit()
        print("Mock buyers created successfully!")
        
        # Create mock mortgage applications
        applications = [
            {
                'borrower_id': 1,
                'lender_id': 1,
                'listing_id': 1,
                'requested_amount': 7000000,
                'repayment_years': 20,
                'status': ApplicationStatus.PENDING,
                'notes': 'First-time homebuyer with stable income'
            },
            {
                'borrower_id': 2,
                'lender_id': 2,
                'listing_id': 2,
                'requested_amount': 12000000,
                'repayment_years': 25,
                'status': ApplicationStatus.APPROVED,
                'notes': 'Excellent credit history'
            },
            {
                'borrower_id': 3,
                'lender_id': 1,
                'listing_id': 3,
                'requested_amount': 4500000,
                'repayment_years': 15,
                'status': ApplicationStatus.NEEDS_INFO,
                'notes': 'Additional documentation required'
            }
        ]
        
        for app_data in applications:
            application = MortgageApplication(**app_data)
            db.session.add(application)
        
        db.session.commit()
        print("Mock mortgage applications created successfully!")

if __name__ == '__main__':
    seed_lenders()