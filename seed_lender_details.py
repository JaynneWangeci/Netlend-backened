#!/usr/bin/env python3
"""
Seed script to populate lender details with comprehensive information
"""

from app import create_app, db
from models import Lender, KenyanCounty

def seed_lender_details():
    """Add detailed information to existing lenders or create sample lenders"""
    app = create_app()
    with app.app_context():
        try:
            # Sample lender data with comprehensive details
            sample_lenders = [
                {
                    'institution_name': 'Kenya Commercial Bank',
                    'contact_person': 'Sarah Mwangi',
                    'email': 'mortgages@kcb.co.ke',
                    'phone_number': '+254-20-3270000',
                    'business_registration_number': 'C.1/2023',
                    'company_type': 'Commercial Bank',
                    'website': 'https://www.kcbgroup.com',
                    'established_year': 1896,
                    'license_number': 'CBK/BL/001',
                    'street_address': 'Kencom House, Moi Avenue',
                    'city': 'Nairobi',
                    'county': KenyanCounty.NAIROBI,
                    'postal_code': '00100',
                    'secondary_phone': '+254-20-3270001',
                    'customer_service_email': 'customercare@kcb.co.ke',
                    'description': 'Leading commercial bank in East Africa offering comprehensive mortgage solutions',
                    'services_offered': ['Home Loans', 'Construction Loans', 'Refinancing', 'Equity Release'],
                    'operating_hours': {
                        'monday': '8:30 AM - 4:00 PM',
                        'tuesday': '8:30 AM - 4:00 PM',
                        'wednesday': '8:30 AM - 4:00 PM',
                        'thursday': '8:30 AM - 4:00 PM',
                        'friday': '8:30 AM - 4:00 PM',
                        'saturday': '9:00 AM - 12:00 PM',
                        'sunday': 'Closed'
                    }
                },
                {
                    'institution_name': 'Equity Bank',
                    'contact_person': 'James Kiprotich',
                    'email': 'homeloans@equitybank.co.ke',
                    'phone_number': '+254-763-026000',
                    'business_registration_number': 'C.2/2023',
                    'company_type': 'Commercial Bank',
                    'website': 'https://www.equitybank.co.ke',
                    'established_year': 1984,
                    'license_number': 'CBK/BL/002',
                    'street_address': 'Equity Centre, Hospital Road',
                    'city': 'Nairobi',
                    'county': KenyanCounty.NAIROBI,
                    'postal_code': '00100',
                    'secondary_phone': '+254-763-026001',
                    'customer_service_email': 'info@equitybank.co.ke',
                    'description': 'Pan-African financial services provider with affordable mortgage solutions',
                    'services_offered': ['Affordable Housing Loans', 'Diaspora Mortgages', 'Staff Mortgages'],
                    'operating_hours': {
                        'monday': '8:00 AM - 5:00 PM',
                        'tuesday': '8:00 AM - 5:00 PM',
                        'wednesday': '8:00 AM - 5:00 PM',
                        'thursday': '8:00 AM - 5:00 PM',
                        'friday': '8:00 AM - 5:00 PM',
                        'saturday': '8:00 AM - 1:00 PM',
                        'sunday': 'Closed'
                    }
                },
                {
                    'institution_name': 'Stima SACCO',
                    'contact_person': 'Mary Wanjiku',
                    'email': 'loans@stimasacco.com',
                    'phone_number': '+254-20-2711000',
                    'business_registration_number': 'CS/3456/2023',
                    'company_type': 'SACCO',
                    'website': 'https://www.stimasacco.com',
                    'established_year': 1974,
                    'license_number': 'SASRA/DT/SACCO/001',
                    'street_address': 'Stima Plaza, Kolobot Road',
                    'city': 'Nairobi',
                    'county': KenyanCounty.NAIROBI,
                    'postal_code': '00200',
                    'secondary_phone': '+254-20-2711001',
                    'customer_service_email': 'members@stimasacco.com',
                    'description': 'Member-owned financial cooperative serving Kenya Power employees and associates',
                    'services_offered': ['Member Mortgages', 'Development Loans', 'Bridging Finance'],
                    'operating_hours': {
                        'monday': '8:00 AM - 5:00 PM',
                        'tuesday': '8:00 AM - 5:00 PM',
                        'wednesday': '8:00 AM - 5:00 PM',
                        'thursday': '8:00 AM - 5:00 PM',
                        'friday': '8:00 AM - 5:00 PM',
                        'saturday': 'Closed',
                        'sunday': 'Closed'
                    }
                }
            ]
            
            # Check if lenders already exist, if not create them
            for lender_data in sample_lenders:
                existing = Lender.query.filter_by(email=lender_data['email']).first()
                if not existing:
                    lender = Lender(**lender_data)
                    lender.set_password('defaultpass123')  # Set default password
                    lender.verified = True
                    db.session.add(lender)
                    print(f"✓ Created lender: {lender_data['institution_name']}")
                else:
                    # Update existing lender with new details
                    for key, value in lender_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    print(f"✓ Updated lender: {lender_data['institution_name']}")
            
            db.session.commit()
            print("✓ Lender details seeded successfully")
            
        except Exception as e:
            print(f"✗ Seeding failed: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    seed_lender_details()