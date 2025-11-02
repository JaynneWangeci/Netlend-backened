from app import create_app, db
from models import MortgageListing

def calculate_all_monthly_payments():
    """Calculate and save monthly payments for all existing listings"""
    app = create_app()
    with app.app_context():
        listings = MortgageListing.query.all()
        
        for listing in listings:
            loan_amount = float(listing.price_range) - listing.down_payment
            monthly_rate = listing.interest_rate / 100 / 12
            num_payments = listing.repayment_period * 12
            
            if monthly_rate == 0:
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            listing.monthly_payment = round(monthly_payment, 2)
            print(f"Listing {listing.id}: Monthly payment = KSH {listing.monthly_payment:,.2f}")
        
        db.session.commit()
        print("Monthly payments calculated and saved!")

if __name__ == '__main__':
    calculate_all_monthly_payments()