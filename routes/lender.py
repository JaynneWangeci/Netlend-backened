from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lender, MortgageListing, MortgageApplication

lender_bp = Blueprint('lender', __name__)

@lender_bp.route('/<int:lender_id>/mortgages', methods=['GET'])
def get_lender_mortgages(lender_id):
    listings = MortgageListing.query.filter_by(lender_id=lender_id).all()
    
    return jsonify([{
        'id': listing.id,
        'title': listing.property_title,
        'type': listing.property_type.value,
        'location': f"{listing.address}, {listing.county.value}",
        'price': float(listing.price_range),
        'rate': listing.interest_rate,
        'term': listing.repayment_period,
        'status': listing.status.value,
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
    
    applications = MortgageApplication.query.filter_by(lender_id=lender_id).all()
    
    return jsonify([{
        'id': app.id,
        'applicant': f'Buyer {app.borrower_id}',
        'amount': app.requested_amount,
        'status': app.status.value,
        'submittedAt': app.submitted_at.strftime('%Y-%m-%d')
    } for app in applications])