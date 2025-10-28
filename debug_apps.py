from app import create_app, db
from models import MortgageApplication, Buyer, Lender

def debug_applications():
    app = create_app()
    with app.app_context():
        applications = MortgageApplication.query.all()
        print(f"Total applications: {len(applications)}")
        
        for app in applications:
            buyer = Buyer.query.get(app.borrower_id)
            lender = Lender.query.get(app.lender_id)
            print(f"App {app.id}: Buyer {buyer.name if buyer else 'Unknown'} -> Lender {lender.institution_name if lender else 'Unknown'} (ID: {app.lender_id})")

if __name__ == '__main__':
    debug_applications()