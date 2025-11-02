from app import create_app, db
from models import (MortgageListing, ActiveMortgage, MortgageApplication, 
                   Buyer, ApplicationStatus, MortgageStatus, ListingStatus)

def update_test_data():
    app = create_app()
    with app.app_context():
        # Get existing listings
        listings = MortgageListing.query.all()
        
        for i, listing in enumerate(listings):
            if i == 0:  # First listing - ACTIVE (no mortgage)
                listing.status = ListingStatus.ACTIVE
                print(f"Listing {listing.id}: {listing.property_title} -> ACTIVE")
                
            elif i == 1:  # Second listing - ACQUIRED (50% paid)
                listing.status = ListingStatus.ACQUIRED
                
                # Create application if not exists
                app = MortgageApplication.query.filter_by(listing_id=listing.id).first()
                if not app:
                    buyer = Buyer.query.first()
                    app = MortgageApplication(
                        borrower_id=buyer.id,
                        lender_id=listing.lender_id,
                        listing_id=listing.id,
                        requested_amount=float(listing.price_range) * 0.8,
                        repayment_years=listing.repayment_period,
                        status=ApplicationStatus.APPROVED
                    )
                    db.session.add(app)
                    db.session.flush()
                
                # Create/update active mortgage
                mortgage = ActiveMortgage.query.filter_by(application_id=app.id).first()
                if not mortgage:
                    mortgage = ActiveMortgage(
                        application_id=app.id,
                        borrower_id=app.borrower_id,
                        lender_id=listing.lender_id,
                        principal_amount=app.requested_amount,
                        interest_rate=listing.interest_rate,
                        repayment_term=listing.repayment_period * 12,
                        remaining_balance=app.requested_amount * 0.5,  # 50% paid
                        status=MortgageStatus.ACTIVE
                    )
                    db.session.add(mortgage)
                else:
                    mortgage.remaining_balance = mortgage.principal_amount * 0.5
                
                print(f"Listing {listing.id}: {listing.property_title} -> ACQUIRED (50% paid)")
                
            elif i == 2:  # Third listing - SOLD (100% paid)
                listing.status = ListingStatus.SOLD
                
                # Create application if not exists
                app = MortgageApplication.query.filter_by(listing_id=listing.id).first()
                if not app:
                    buyer = Buyer.query.first()
                    app = MortgageApplication(
                        borrower_id=buyer.id,
                        lender_id=listing.lender_id,
                        listing_id=listing.id,
                        requested_amount=float(listing.price_range) * 0.8,
                        repayment_years=listing.repayment_period,
                        status=ApplicationStatus.APPROVED
                    )
                    db.session.add(app)
                    db.session.flush()
                
                # Create/update active mortgage
                mortgage = ActiveMortgage.query.filter_by(application_id=app.id).first()
                if not mortgage:
                    mortgage = ActiveMortgage(
                        application_id=app.id,
                        borrower_id=app.borrower_id,
                        lender_id=listing.lender_id,
                        principal_amount=app.requested_amount,
                        interest_rate=listing.interest_rate,
                        repayment_term=listing.repayment_period * 12,
                        remaining_balance=0,  # 100% paid
                        status=MortgageStatus.COMPLETED
                    )
                    db.session.add(mortgage)
                else:
                    mortgage.remaining_balance = 0
                    mortgage.status = MortgageStatus.COMPLETED
                
                print(f"Listing {listing.id}: {listing.property_title} -> SOLD (100% paid)")
        
        db.session.commit()
        print("\nTest data updated successfully!")
        
        # Show final status
        print("\nFinal status summary:")
        for listing in MortgageListing.query.all():
            print(f"ID {listing.id}: {listing.property_title} - {listing.status.value}")

if __name__ == '__main__':
    update_test_data()