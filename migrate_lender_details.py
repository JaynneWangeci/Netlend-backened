#!/usr/bin/env python3
"""
Migration script to add new lender detail fields to the database
"""

from app import create_app, db
from models import Lender

def migrate_lender_details():
    """Add new columns to lenders table"""
    app = create_app()
    with app.app_context():
        try:
            # Create all tables with new schema
            db.create_all()
            print("✓ Database schema updated successfully")
            
            # Update existing lenders with default values if needed
            lenders = Lender.query.all()
            for lender in lenders:
                if not lender.company_type:
                    lender.company_type = "Bank"
                if not lender.services_offered:
                    lender.services_offered = ["Mortgage Loans", "Home Financing"]
                if not lender.operating_hours:
                    lender.operating_hours = {
                        "monday": "8:00 AM - 5:00 PM",
                        "tuesday": "8:00 AM - 5:00 PM",
                        "wednesday": "8:00 AM - 5:00 PM",
                        "thursday": "8:00 AM - 5:00 PM",
                        "friday": "8:00 AM - 5:00 PM",
                        "saturday": "9:00 AM - 1:00 PM",
                        "sunday": "Closed"
                    }
            
            db.session.commit()
            print(f"✓ Updated {len(lenders)} existing lender records")
            
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_lender_details()