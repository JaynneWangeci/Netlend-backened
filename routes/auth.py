from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import Lender


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/debug', methods=['POST'])
def debug():
    data = request.get_json()
    print(f"Debug - Received data: {data}")
    return jsonify({'received': data}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Registration data: {data}")
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType') or data.get('user_type', 'lender')
        
        if not email or not password:
            return jsonify({'message': 'Email and password required'}), 400
        
        # Check if user exists in any table
        from models import User, UserRole, Buyer
        if (User.query.filter_by(email=email).first() or 
            Lender.query.filter_by(email=email).first() or
            Buyer.query.filter_by(email=email).first()):
            return jsonify({'message': 'Email already registered'}), 400
        
        name = data.get('full_name') or data.get('name') or data.get('institution_name') or 'User'
        
        if user_type in ['homebuyer', 'buyer']:
            # Create in Buyer table for homebuyers
            buyer = Buyer(
                name=name,
                email=email,
                phone_number=data.get('phone') or data.get('phone_number'),
                verified=True
            )
            buyer.set_password(password)
            db.session.add(buyer)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Buyer registration successful'}), 201
        else:
            # Create in Lender table for lenders
            lender = Lender(
                email=email,
                institution_name=name,
                contact_person=name,
                phone_number=data.get('phone') or data.get('phone_number'),
                verified=True
            )
            lender.set_password(password)
            db.session.add(lender)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Lender registration successful'}), 201
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    from models import Buyer
    
    # Check buyer first
    buyer = Buyer.query.filter_by(email=email).first()
    if buyer and buyer.check_password(password):
        access_token = create_access_token(identity=f"B{buyer.id}")
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': buyer.id,
                'email': buyer.email,
                'name': buyer.name,
                'userType': 'homebuyer'
            }
        }), 200
    
    # Check lender
    lender = Lender.query.filter_by(email=email).first()
    if lender and lender.check_password(password):
        access_token = create_access_token(identity=f"L{lender.id}")
        return jsonify({
            'access_token': access_token,
            'lender': {
                'id': lender.id,
                'email': lender.email,
                'institution_name': lender.institution_name,
                'contact_person': lender.contact_person
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

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