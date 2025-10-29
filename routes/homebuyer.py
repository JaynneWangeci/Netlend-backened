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
        if 'nationalId' in data:
            buyer.national_id = data['nationalId']
        if 'gender' in data:
            buyer.gender = data['gender']
        if 'maritalStatus' in data:
            buyer.marital_status = data['maritalStatus']
        if 'dependents' in data:
            buyer.dependents = int(data['dependents']) if data['dependents'] else 0
        
        # Employment & Income
        if 'employmentStatus' in data:
            buyer.employment_status = data['employmentStatus']
        if 'employerName' in data:
            buyer.employer_name = data['employerName'] if data['employerName'] else None
        if 'monthlyGrossIncome' in data:
            buyer.monthly_gross_income = float(data['monthlyGrossIncome']) if data['monthlyGrossIncome'] else None
        if 'monthlyNetIncome' in data:
            buyer.monthly_net_income = float(data['monthlyNetIncome']) if data['monthlyNetIncome'] else None
        
        # Banking Information
        if 'bankName' in data:
            buyer.bank_name = data['bankName']
        if 'accountNumber' in data:
            buyer.account_number = data['accountNumber']
        
        # Calculate creditworthiness score
        if buyer.calculate_creditworthiness_score:
            buyer.calculate_creditworthiness_score()
        
        db.session.add(buyer)
        db.session.commit()
        return jsonify({
            'success': True,
            'profileComplete': buyer.profile_complete,
            'creditworthinessScore': buyer.creditworthiness_score
        })
    except Exception as e:
        print(f'Profile update error: {e}')
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@homebuyer_bp.route('/creditworthiness', methods=['GET'])
@jwt_required()
def get_creditworthiness():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404
    
    score = buyer.calculate_creditworthiness_score()
    db.session.commit()
    
    return jsonify({
        'score': score,
        'riskLevel': 'Low Risk' if score >= 80 else 'Medium Risk',
        'recommendation': 'Good candidate',
        'profileComplete': buyer.profile_complete
    })