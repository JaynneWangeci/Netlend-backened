from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, MortgageListing, UserRole
from utils.cloudinary import upload_images

mortgages_bp = Blueprint('mortgages', __name__)

@mortgages_bp.route('/', methods=['GET'])
def get_mortgages():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    mortgages = MortgageListing.query.filter_by(is_active=True).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'mortgages': [{
            'id': m.id,
            'title': m.title,
            'property_type': m.property_type,
            'location': m.location,
            'price': float(m.price),
            'interest_rate': float(m.interest_rate),
            'repayment_period': m.repayment_period,
            'down_payment': float(m.down_payment),
            'minimum_income': float(m.minimum_income),
            'images': m.images,
            'lender_name': m.lender.full_name
        } for m in mortgages.items],
        'total': mortgages.total,
        'pages': mortgages.pages,
        'current_page': page
    }), 200

@mortgages_bp.route('/', methods=['POST'])
@jwt_required()
def create_mortgage():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != UserRole.LENDER:
        return jsonify({'message': 'Only lenders can create mortgage listings'}), 403
    
    data = request.get_json()
    
    mortgage = MortgageListing(
        title=data['title'],
        property_type=data['property_type'],
        location=data['location'],
        price=data['price'],
        interest_rate=data['interest_rate'],
        repayment_period=data['repayment_period'],
        down_payment=data['down_payment'],
        minimum_income=data['minimum_income'],
        description=data.get('description'),
        lender_id=user_id
    )
    
    if 'images' in data:
        mortgage.images = upload_images(data['images'])
    
    db.session.add(mortgage)
    db.session.commit()
    
    return jsonify({'message': 'Mortgage listing created successfully', 'id': mortgage.id}), 201

@mortgages_bp.route('/<int:mortgage_id>', methods=['GET'])
def get_mortgage(mortgage_id):
    mortgage = MortgageListing.query.get_or_404(mortgage_id)
    
    return jsonify({
        'id': mortgage.id,
        'title': mortgage.title,
        'property_type': mortgage.property_type,
        'location': mortgage.location,
        'price': float(mortgage.price),
        'interest_rate': float(mortgage.interest_rate),
        'repayment_period': mortgage.repayment_period,
        'down_payment': float(mortgage.down_payment),
        'minimum_income': float(mortgage.minimum_income),
        'description': mortgage.description,
        'images': mortgage.images,
        'lender': {
            'id': mortgage.lender.id,
            'name': mortgage.lender.full_name,
            'email': mortgage.lender.email
        }
    }), 200

@mortgages_bp.route('/my-listings', methods=['GET'])
@jwt_required()
def get_my_listings():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != UserRole.LENDER:
        return jsonify({'message': 'Only lenders can view listings'}), 403
    
    mortgages = MortgageListing.query.filter_by(lender_id=user_id).all()
    
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'property_type': m.property_type,
        'location': m.location,
        'price': float(m.price),
        'interest_rate': float(m.interest_rate),
        'is_active': m.is_active
    } for m in mortgages]), 200