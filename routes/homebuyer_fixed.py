from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, MortgageApplication, MortgageListing, Lender, Buyer, KenyanCounty, PropertyType
from datetime import datetime

homebuyer_bp = Blueprint('homebuyer', __name__)

@homebuyer_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
        buyer = Buyer.query.get(buyer_id)
        
        if not buyer:
            return jsonify({'error': 'Buyer not found'}), 404
            
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Personal Information
        if 'name' in data:
            buyer.name = data['name']
        if 'phoneNumber' in data:
            buyer.phone_number = data['phoneNumber']
        
        # Calculate creditworthiness score
        buyer.calculate_creditworthiness_score()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'profileComplete': buyer.profile_complete,
            'creditworthinessScore': buyer.creditworthiness_score
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500