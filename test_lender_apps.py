from app import create_app, db
from models import MortgageApplication, Buyer

def test_lender_apps():
    app = create_app()
    with app.app_context():
        # Test lender ID 1 applications
        applications = MortgageApplication.query.filter_by(lender_id=1).all()
        print(f"Applications for lender ID 1: {len(applications)}")
        
        for app in applications:
            buyer = Buyer.query.filter_by(id=app.borrower_id).first()
            print(f"App {app.id}: Amount {app.requested_amount}, Status {app.status.value}, Buyer: {buyer.name if buyer else 'Not found'}")

if __name__ == '__main__':
    test_lender_apps()