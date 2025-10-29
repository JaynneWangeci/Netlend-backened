from app import create_app, db
from models import MortgageListing, ActiveMortgage, MortgageApplication, ListingStatus

def update_existing_house_statuses():
    """Update status of existing houses based on payment progress"""
    app = create_app()
    with app.app_context():
        # Get all active mortgages
        active_mortgages = ActiveMortgage.query.all()
        
        for mortgage in active_mortgages:
            if mortgage.application and mortgage.application.listing:
                listing = mortgage.application.listing
                
                # Calculate payment percentage
                total_paid = mortgage.principal_amount - mortgage.remaining_balance
                payment_percentage = total_paid / mortgage.principal_amount
                
                # Update status based on payment
                if payment_percentage >= 1.0:
                    listing.status = ListingStatus.SOLD
                    print(f"House '{listing.property_title}' marked as SOLD (100% paid)")
                elif payment_percentage > 0:
                    listing.status = ListingStatus.ACQUIRED
                    print(f"House '{listing.property_title}' marked as ACQUIRED ({payment_percentage:.1%} paid)")
                else:
                    listing.status = ListingStatus.ACTIVE
                    print(f"House '{listing.property_title}' remains ACTIVE (0% paid)")
        
        db.session.commit()
        print("House statuses updated successfully!")

if __name__ == '__main__':
    update_existing_house_statuses()