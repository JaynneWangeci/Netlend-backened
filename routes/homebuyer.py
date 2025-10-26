from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, MortgageApplication, MortgageListing, Lender, Buyer
from datetime import datetime

homebuyer_bp = Blueprint('homebuyer', __name__)

@homebuyer_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    applications = MortgageApplication.query.filter_by(borrower_id=int(user_id)).all()
    
    return jsonify({
        'totalApplications': len(applications),
        'activeApplications': len([a for a in applications if a.status.value == 'pending']),
        'approvedApplications': len([a for a in applications if a.status.value == 'approved']),
        'savedProperties': 0,
        'preApprovalStatus': 'pending'
    })

@homebuyer_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    applications = MortgageApplication.query.filter_by(borrower_id=buyer_id).all()
    
    return jsonify([{
        'id': app.id,
        'lender': app.lender.institution_name,
        'amount': app.requested_amount,
        'status': app.status.value,
        'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
        'property': f'Property {app.listing_id}'
    } for app in applications])

@homebuyer_bp.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    user_id = get_jwt_identity()
    data = request.json
    
    application = MortgageApplication(
        borrower_id=int(user_id),
        lender_id=data['lenderId'],
        listing_id=data['listingId'],
        requested_amount=data['loanAmount'],
        repayment_years=data['repaymentYears']
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'id': application.id, 'status': 'submitted'}), 201

@homebuyer_bp.route('/properties', methods=['GET'])
def get_properties():
    listings = MortgageListing.query.all()
    
    return jsonify([{
        'id': listing.id,
        'title': listing.property_title,
        'type': listing.property_type.value,
        'location': f"{listing.address}, {listing.county.value}",
        'price': float(listing.price_range),
        'rate': listing.interest_rate,
        'term': listing.repayment_period,
        'lender': listing.lender.institution_name,
        'images': listing.images or []
    } for listing in listings])

@homebuyer_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    return jsonify({
        'id': buyer.id,
        'name': buyer.name,
        'email': buyer.email,
        'verified': buyer.verified,
        'profileComplete': True
    })

@homebuyer_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.json
    user = User.query.get(int(user_id))
    
    if 'name' in data:
        user.name = data['name']
    
    db.session.commit()
    return jsonify({'success': True})

@homebuyer_bp.route('/prequalify', methods=['POST'])
@jwt_required()
def prequalify():
    data = request.json
    
    # Simple eligibility calculation
    income = data.get('income', 0)
    loan_amount = data.get('loanAmount', 0)
    
    eligibility_score = min(90, (income * 12 * 5) / loan_amount * 100) if loan_amount > 0 else 0
    
    return jsonify({
        'eligibilityScore': round(eligibility_score),
        'maxLoanAmount': income * 12 * 5,
        'status': 'qualified' if eligibility_score > 70 else 'review_required'
    })

@homebuyer_bp.route('/lenders', methods=['GET'])
def get_lenders():
    lenders = Lender.query.filter_by(verified=True).all()
    
    return jsonify([{
        'id': lender.id,
        'name': lender.institution_name,
        'email': lender.email,
        'verified': lender.verified
    } for lender in lenders])

@homebuyer_bp.route('/pre-approval', methods=['GET'])
@jwt_required()
def get_pre_approval():
    return jsonify({
        'status': 'pending',
        'amount': 0,
        'expiryDate': None
    })

@homebuyer_bp.route('/saved-properties', methods=['GET'])
@jwt_required()
def get_saved_properties():
    return jsonify([])

