# NetLend Backend - Lender Routes
# This module handles all lender-specific functionality including:
# - Lender dashboard with key metrics and statistics
# - Mortgage listing management (create, read, update, delete)
# - Mortgage application processing and approval workflow
# - Buyer information access for application review
# - Active mortgage tracking and sold mortgage management
# - Lender profile management and business information

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity  # Authentication
from app import db  # Database instance
from models import Lender, MortgageListing, MortgageApplication, Buyer, ApplicationStatus, ActiveMortgage, ListingStatus
from datetime import datetime, timedelta  # Date calculations for mortgage terms

# Create Blueprint for lender routes with URL prefix /api/lender
lender_bp = Blueprint('lender', __name__)

@lender_bp.route('/mortgages', methods=['GET'])
@jwt_required()
def get_my_mortgages():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    
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
    
    return jsonify({
        'totalListings': listings,
        'totalApplications': applications,
        'activeLoans': 0,
        'revenue': 0
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
        return jsonify({'success': True})
    except Exception as e:
        print(f"Database commit failed: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@lender_bp.route('/applications/<int:app_id>/approve', methods=['POST'])
@jwt_required()  # Requires lender authentication
def approve_application(app_id):
    """LENDER ENDPOINT: Approve mortgage application with automatic workflow
    
    This endpoint handles the complete mortgage approval workflow:
    
    APPROVAL PROCESS:
    1. Validates lender ownership of the application
    2. Approves the selected application
    3. Automatically rejects all other pending applications for the same property
    4. Updates property status from ACTIVE to ACQUIRED
    5. Creates ActiveMortgage record for payment tracking
    6. Sets up initial payment schedule
    
    BUSINESS LOGIC:
    - Only one application can be approved per property
    - All other applications are automatically rejected to prevent conflicts
    - Property becomes unavailable for new applications
    - Mortgage tracking begins immediately
    
    INTEGRATION POINTS:
    - Updates buyer's "My Mortgages" section
    - Updates lender's "Sold Mortgages" section
    - Removes property from public browsing (no longer ACTIVE)
    - Triggers payment schedule generation
    
    Returns: Success confirmation with active mortgage details
    """
    try:
        # Extract and validate lender ID from JWT token
        user_id = get_jwt_identity()
        lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
        
        # Fetch the mortgage application
        application = MortgageApplication.query.get_or_404(app_id)
        
        # Security check: Ensure lender owns this application
        if application.lender_id != lender_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # STEP 1: Approve the selected application
        application.status = ApplicationStatus.APPROVED
        
        # STEP 2: Automatically reject all other pending applications for the same property
        # This prevents multiple approvals for the same property and ensures data consistency
        other_apps = MortgageApplication.query.filter(
            MortgageApplication.listing_id == application.listing_id,  # Same property
            MortgageApplication.id != app_id,  # Exclude the approved application
            MortgageApplication.status == ApplicationStatus.PENDING  # Only pending applications
        ).all()
        
        # Mark all other applications as rejected
        for other_app in other_apps:
            other_app.status = ApplicationStatus.REJECTED
        
        # STEP 3: Update property status to ACQUIRED
        # This removes the property from public browsing and marks it as sold
        if application.listing:
            application.listing.status = ListingStatus.ACQUIRED
        
        # STEP 4: Create ActiveMortgage record for payment tracking
        # This record will be used to track payments, calculate balances, and manage the mortgage lifecycle
        active_mortgage = ActiveMortgage(
            application_id=application.id,  # Link to original application
            borrower_id=application.borrower_id,  # Buyer who will make payments
            lender_id=application.lender_id,  # Lender who will receive payments
            principal_amount=application.requested_amount,  # Original loan amount
            interest_rate=application.listing.interest_rate if application.listing else 12.0,  # Annual rate
            repayment_term=application.repayment_years * 12,  # Convert years to months
            remaining_balance=application.requested_amount,  # Initially equals principal
            next_payment_due=datetime.now().date() + timedelta(days=30)  # First payment in 30 days
        )
        
        db.session.add(active_mortgage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Application approved. {len(other_apps)} other applications rejected.',
            'activemortgage': {
                'id': active_mortgage.id,
                'principalAmount': active_mortgage.principal_amount,
                'remainingBalance': active_mortgage.remaining_balance
            }
        })
    except Exception as e:
        db.session.rollback()
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