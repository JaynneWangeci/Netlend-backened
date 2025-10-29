from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lender, MortgageListing, MortgageApplication, Buyer

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
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    print(f"Debug: user_id={user_id}, lender_id={lender_id}")
    
    applications = MortgageApplication.query.filter_by(lender_id=lender_id).all()
    print(f"Debug: Found {len(applications)} applications for lender {lender_id}")
    
    result = []
    for app in applications:
        buyer = Buyer.query.get(app.borrower_id)
        result.append({
            'id': app.id,
            'applicant': buyer.name if buyer else f'Buyer {app.borrower_id}',
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
        result.append({
            'id': app.id,
            'applicant': buyer.name if buyer else f'Buyer {app.borrower_id}',
            'applicantName': buyer.name if buyer else f'Buyer {app.borrower_id}',
            'buyerName': buyer.name if buyer else f'Buyer {app.borrower_id}',
            'name': buyer.name if buyer else f'Buyer {app.borrower_id}',
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