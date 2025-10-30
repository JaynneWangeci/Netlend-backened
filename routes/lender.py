from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lender, MortgageListing, MortgageApplication, Buyer, ApplicationStatus, ActiveMortgage, ListingStatus, PaymentSchedule
from datetime import datetime, timedelta

lender_bp = Blueprint('lender', __name__)

@lender_bp.route('/<int:lender_id>/mortgages', methods=['GET'])
def get_lender_mortgages(lender_id):
    listings = MortgageListing.query.filter_by(lender_id=lender_id).all()
    
    return jsonify([{
        'id': listing.id,
        'title': listing.property_title,
        'type': listing.property_type.value,
        'bedrooms': listing.bedrooms,
        'location': f"{listing.address}, {listing.county.value}",
        'price': float(listing.price_range),
        'rate': listing.interest_rate,
        'term': listing.repayment_period,
        'status': listing.status.value,
        'editable': listing.status.value == 'active',
        'images': listing.images if listing.images else [],
        'createdAt': listing.created_at.strftime('%Y-%m-%d')
    } for listing in listings])

@lender_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    
    listings = MortgageListing.query.filter_by(lender_id=lender_id).count()
    applications = MortgageApplication.query.filter_by(lender_id=lender_id).count()
    active_loans = ActiveMortgage.query.filter_by(lender_id=lender_id).count()
    
    # Calculate revenue from payments
    revenue = 0
    mortgages = ActiveMortgage.query.filter_by(lender_id=lender_id).all()
    for mortgage in mortgages:
        payments = PaymentSchedule.query.filter_by(mortgage_id=mortgage.id).all()
        for payment in payments:
            if payment.status.value == 'paid':
                # Calculate interest portion (simplified)
                interest_portion = payment.amount_paid * (mortgage.interest_rate / 100 / 12)
                revenue += interest_portion
    
    return jsonify({
        'totalListings': listings,
        'totalApplications': applications,
        'activeLoans': active_loans,
        'revenue': round(revenue, 2)
    })

@lender_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()
    if isinstance(user_id, str) and len(user_id) > 1 and user_id[0] in ['L', 'B', 'A', 'U']:
        lender_id = int(user_id[1:])
    else:
        lender_id = int(user_id)
    print(f"Debug: user_id={user_id}, lender_id={lender_id}")
    
    applications = MortgageApplication.query.filter_by(lender_id=lender_id).all()
    print(f"Debug: Found {len(applications)} applications for lender {lender_id}")
    
    result = []
    for app in applications:
        buyer = Buyer.query.get(app.borrower_id)
        # If no buyer found, check if it's a lender testing (fallback)
        if not buyer:
            lender = Lender.query.get(app.borrower_id)
            applicant_name = lender.institution_name if lender else f'User {app.borrower_id}'
            phone = lender.phone_number if lender else 'N/A'
            email = lender.email if lender else 'N/A'
            monthly_income = 'N/A'
            employment_status = 'N/A'
        else:
            applicant_name = buyer.name
            phone = buyer.phone_number or 'N/A'
            email = buyer.email or 'N/A'
            monthly_income = buyer.monthly_net_income or 'N/A'
            employment_status = buyer.employment_status or 'N/A'
            
        result.append({
            'id': app.id,
            'applicant': applicant_name,
            'phone': phone,
            'email': email,
            'monthlyIncome': monthly_income,
            'employmentStatus': employment_status,
            'amount': app.requested_amount,
            'status': app.status.value,
            'property': app.listing.property_title if app.listing else 'Unknown Property',
            'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
            'notes': app.notes
        })
    return jsonify(result)

@lender_bp.route('/<int:lender_id>/applications', methods=['GET'])
def get_lender_applications(lender_id):
    print(f"Debug: Direct lender_id={lender_id}")
    applications = MortgageApplication.query.filter_by(lender_id=lender_id).all()
    print(f"Debug: Found {len(applications)} applications for lender {lender_id}")
    
    result = []
    for app in applications:
        buyer = Buyer.query.get(app.borrower_id)
        # If no buyer found, check if it's a lender testing (fallback)
        if not buyer:
            lender = Lender.query.get(app.borrower_id)
            applicant_name = lender.institution_name if lender else f'User {app.borrower_id}'
            phone = lender.phone_number if lender else 'N/A'
            email = lender.email if lender else 'N/A'
            monthly_income = 'N/A'
            employment_status = 'N/A'
        else:
            applicant_name = buyer.name
            phone = buyer.phone_number or 'N/A'
            email = buyer.email or 'N/A'
            monthly_income = buyer.monthly_net_income or 'N/A'
            employment_status = buyer.employment_status or 'N/A'
            
        result.append({
            'id': app.id,
            'applicant': applicant_name,
            'applicantName': applicant_name,
            'buyerName': applicant_name,
            'name': applicant_name,
            'phone': phone,
            'email': email,
            'monthlyIncome': monthly_income,
            'employmentStatus': employment_status,
            'amount': app.requested_amount,
            'status': app.status.value,
            'property': app.listing.property_title if app.listing else 'Unknown Property',
            'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
            'notes': app.notes
        })
    return jsonify(result)

@lender_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_lender_profile():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    lender = Lender.query.get(lender_id)
    
    return jsonify({
        'id': lender.id,
        'institution_name': lender.institution_name,
        'contact_person': lender.contact_person,
        'email': lender.email,
        'phone_number': lender.phone_number,
        'business_registration_number': lender.business_registration_number,
        'verified': lender.verified,
        'logo_url': lender.logo_url
    })

@lender_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_lender_profile():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    lender = Lender.query.get(lender_id)
    data = request.json
    
    print(f"Debug: Received data: {data}")  # Debug log
    
    if 'company_name' in data:
        lender.institution_name = data['company_name']
    if 'institution_name' in data:
        lender.institution_name = data['institution_name']
        print(f"Updated institution_name to: {data['institution_name']}")
    if 'contact_person' in data:
        lender.contact_person = data['contact_person']
    if 'contact_email' in data:
        lender.email = data['contact_email']
    if 'email' in data:
        lender.email = data['email']
    if 'phone' in data:
        lender.phone_number = data['phone']
    if 'phone_number' in data:
        lender.phone_number = data['phone_number']
    if 'license_number' in data:
        lender.business_registration_number = data['license_number']
    if 'business_registration_number' in data:
        lender.business_registration_number = data['business_registration_number']
    if 'address' in data:
        # Note: address field doesn't exist in Lender model, ignoring for now
        print(f"Address field received but not saved: {data['address']}")
    if 'logo_url' in data:
        lender.logo_url = data['logo_url']
    
    try:
        db.session.commit()
        print("Database commit successful")
        return jsonify({
            'success': True,
            'modal': {
                'type': 'success',
                'title': 'Profile Updated',
                'message': 'Your profile has been updated successfully.'
            }
        })
    except Exception as e:
        print(f"Database commit failed: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'modal': {
                'type': 'error',
                'title': 'Update Failed',
                'message': 'Failed to update profile. Please try again.',
                'error': str(e)
            }
        }), 500

@lender_bp.route('/applications/<int:app_id>/approve', methods=['POST'])
@jwt_required()
def approve_application(app_id):
    try:
        user_id = get_jwt_identity()
        lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
        
        # Get the application
        application = MortgageApplication.query.get_or_404(app_id)
        
        # Verify lender owns this application
        if application.lender_id != lender_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Approve this application
        application.status = ApplicationStatus.APPROVED
        
        # Reject all other applications for the same property
        other_apps = MortgageApplication.query.filter(
            MortgageApplication.listing_id == application.listing_id,
            MortgageApplication.id != app_id,
            MortgageApplication.status == ApplicationStatus.PENDING
        ).all()
        
        for other_app in other_apps:
            other_app.status = ApplicationStatus.REJECTED
        
        # Update property status to acquired
        if application.listing:
            application.listing.status = ListingStatus.ACQUIRED
        
        # Create active mortgage
        active_mortgage = ActiveMortgage(
            application_id=application.id,
            borrower_id=application.borrower_id,
            lender_id=application.lender_id,
            principal_amount=application.requested_amount,
            interest_rate=application.listing.interest_rate if application.listing else 12.0,
            repayment_term=application.repayment_years * 12,
            remaining_balance=application.requested_amount,
            next_payment_due=datetime.now().date() + timedelta(days=30)
        )
        
        db.session.add(active_mortgage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'modal': {
                'type': 'success',
                'title': 'Application Approved',
                'message': f'Application has been approved successfully. {len(other_apps)} other applications were automatically rejected.',
                'details': {
                    'mortgage_id': active_mortgage.id,
                    'principal_amount': active_mortgage.principal_amount,
                    'remaining_balance': active_mortgage.remaining_balance
                }
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lender_bp.route('/my-listings', methods=['GET'])
@jwt_required()
def get_my_listings():
    """Get all property listings for the current lender"""
    try:
        user_id = get_jwt_identity()
        lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
        
        listings = MortgageListing.query.filter_by(lender_id=lender_id).all()
        
        result = []
        for listing in listings:
            # Count applications for this listing
            applications_count = MortgageApplication.query.filter_by(listing_id=listing.id).count()
            
            result.append({
                'id': listing.id,
                'title': listing.property_title,
                'type': listing.property_type.value,
                'bedrooms': listing.bedrooms,
                'location': f"{listing.address}, {listing.county.value}",
                'price': float(listing.price_range),
                'interestRate': listing.interest_rate,
                'repaymentPeriod': listing.repayment_period,
                'downPayment': listing.down_payment,
                'monthlyPayment': listing.monthly_payment,
                'status': listing.status.value,
                'applicationsCount': applications_count,
                'images': listing.images or [],
                'createdAt': listing.created_at.strftime('%Y-%m-%d'),
                'eligibilityCriteria': listing.eligibility_criteria
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lender_bp.route('/sold-mortgages', methods=['GET'])
@jwt_required()
def get_sold_mortgages():
    try:
        user_id = get_jwt_identity()
        lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
        
        active_mortgages = ActiveMortgage.query.filter_by(lender_id=lender_id).all()
        
        result = []
        for mortgage in active_mortgages:
            buyer = Buyer.query.get(mortgage.borrower_id)
            property_title = mortgage.application.listing.property_title if mortgage.application and mortgage.application.listing else 'Unknown Property'
            
            result.append({
                'id': mortgage.id,
                'buyer': buyer.name if buyer else f'Buyer {mortgage.borrower_id}',
                'property': property_title,
                'principalAmount': mortgage.principal_amount,
                'remainingBalance': mortgage.remaining_balance,
                'interestRate': mortgage.interest_rate,
                'status': mortgage.status.value,
                'startDate': mortgage.created_at.strftime('%Y-%m-%d'),
                'nextPaymentDue': mortgage.next_payment_due.isoformat() if mortgage.next_payment_due else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500