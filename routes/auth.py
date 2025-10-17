from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import Lender
from utils.email import send_verification_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if Lender.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    lender = Lender(
        email=data['email'],
        institution_name=data['institution_name'],
        contact_person=data['contact_person'],
        phone_number=data.get('phone_number'),
        business_registration_number=data.get('business_registration_number')
    )
    lender.set_password(data['password'])
    
    db.session.add(lender)
    db.session.commit()
    
    send_verification_email(lender.email, lender.id)
    
    return jsonify({'message': 'Registration successful. Please verify your email.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    lender = Lender.query.filter_by(email=data['email']).first()
    
    if not lender or not lender.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not lender.verified:
        return jsonify({'message': 'Please verify your email first'}), 401
    
    access_token = create_access_token(identity=lender.id)
    
    return jsonify({
        'access_token': access_token,
        'lender': {
            'id': lender.id,
            'email': lender.email,
            'institution_name': lender.institution_name,
            'contact_person': lender.contact_person
        }
    }), 200

@auth_bp.route('/verify/<int:lender_id>', methods=['GET'])
def verify_email(lender_id):
    lender = Lender.query.get_or_404(lender_id)
    lender.verified = True
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    lender_id = get_jwt_identity()
    lender = Lender.query.get_or_404(lender_id)
    
    return jsonify({
        'id': lender.id,
        'email': lender.email,
        'institution_name': lender.institution_name,
        'contact_person': lender.contact_person,
        'phone_number': lender.phone_number,
        'business_registration_number': lender.business_registration_number,
        'verified': lender.verified
    }), 200