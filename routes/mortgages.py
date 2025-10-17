from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lender, MortgageListing
from utils.cloudinary import upload_images

mortgages_bp = Blueprint('mortgages', __name__)

@mortgages_bp.route('/', methods=['GET'])
def get_mortgages():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    mortgages = MortgageListing.query.filter_by(status='active').paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'mortgages': [{
            'id': m.id,
            'property_title': m.property_title,
            'property_type': m.property_type.value,
            'location': m.location,
            'price_range': float(m.price_range),
            'interest_rate': m.interest_rate,
            'repayment_period': m.repayment_period,
            'down_payment': m.down_payment,
            'eligibility_criteria': m.eligibility_criteria,
            'images': m.images,
            'lender_name': m.lender.institution_name
        } for m in mortgages.items],
        'total': mortgages.total,
        'pages': mortgages.pages,
        'current_page': page
    }), 200

@mortgages_bp.route('/', methods=['POST'])
@jwt_required()
def create_mortgage():
    lender_id = get_jwt_identity()
    lender = Lender.query.get_or_404(lender_id)
    
    data = request.get_json()
    
    mortgage = MortgageListing(
        property_title=data['property_title'],
        property_type=data['property_type'],
        location=data['location'],
        price_range=data['price_range'],
        interest_rate=data['interest_rate'],
        repayment_period=data['repayment_period'],
        down_payment=data['down_payment'],
        eligibility_criteria=data.get('eligibility_criteria'),
        lender_id=lender_id
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
        'property_title': mortgage.property_title,
        'property_type': mortgage.property_type.value,
        'location': mortgage.location,
        'price_range': float(mortgage.price_range),
        'interest_rate': mortgage.interest_rate,
        'repayment_period': mortgage.repayment_period,
        'down_payment': mortgage.down_payment,
        'eligibility_criteria': mortgage.eligibility_criteria,
        'images': mortgage.images,
        'lender': {
            'id': mortgage.lender.id,
            'institution_name': mortgage.lender.institution_name,
            'email': mortgage.lender.email
        }
    }), 200

@mortgages_bp.route('/my-listings', methods=['GET'])
@jwt_required()
def get_my_listings():
    lender_id = get_jwt_identity()
    lender = Lender.query.get_or_404(lender_id)
    
    mortgages = MortgageListing.query.filter_by(lender_id=lender_id).all()
    
    return jsonify([{
        'id': m.id,
        'property_title': m.property_title,
        'property_type': m.property_type.value,
        'location': m.location,
        'price_range': float(m.price_range),
        'interest_rate': m.interest_rate,
        'status': m.status.value
    } for m in mortgages]), 200