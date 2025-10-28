from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lender, MortgageListing
# from utils.cloudinary import upload_images

mortgages_bp = Blueprint('mortgages', __name__)

@mortgages_bp.route('/debug', methods=['POST'])
def debug_mortgage():
    data = request.get_json()
    print(f"Debug - Received: {data}")
    return jsonify({'received': data, 'status': 'ok'}), 200

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
            'bedrooms': m.bedrooms,
            'address': m.address,
            'county': m.county.value,
            'price_range': f"KSH {float(m.price_range):,.2f}",
            'interest_rate': m.interest_rate,
            'repayment_period': m.repayment_period,
            'down_payment': f"KSH {m.down_payment:,.2f}",
            'eligibility_criteria': m.eligibility_criteria,
            'images': m.images,
            'lender_name': m.lender.institution_name
        } for m in mortgages.items],
        'total': mortgages.total,
        'pages': mortgages.pages,
        'current_page': page
    }), 200

@mortgages_bp.route('/', methods=['POST'])
def create_mortgage():
    try:
        lender_id = 1  # Hardcoded for testing
        data = request.get_json()
        print(f"Creating mortgage with data: {data}")  # Debug log
        
        mortgage = MortgageListing(
            property_title=data.get('subject', 'Default Title'),
            property_type=data.get('property_type', 'apartment').upper(),
            bedrooms=data.get('bedrooms', 3),
            address=data.get('address', 'Default Address'),
            county=data.get('county', 'Nairobi').upper().replace(' ', '_'),
            price_range=data.get('price_range', 1000000),
            interest_rate=data.get('interest_rate', 12.0),
            repayment_period=data.get('repayment_period', 25),
            down_payment=data.get('down_payment', 200000),
            eligibility_criteria=data.get('eligibility_criteria', ''),
            images=data.get('images', []),
            lender_id=lender_id
        )
        
        db.session.add(mortgage)
        db.session.commit()
        
        return jsonify({'message': 'Mortgage listing created successfully', 'id': mortgage.id}), 201
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@mortgages_bp.route('/lender/<int:lender_id>/mortgages', methods=['GET'])
def get_lender_mortgages(lender_id):
    try:
        mortgages = MortgageListing.query.filter_by(lender_id=lender_id).all()
        
        result = []
        for m in mortgages:
            try:
                result.append({
                    'id': m.id,
                    'property_title': m.property_title,
                    'property_type': str(m.property_type.value) if hasattr(m.property_type, 'value') else str(m.property_type),
                    'bedrooms': m.bedrooms,
                    'address': m.address,
                    'county': str(m.county.value) if hasattr(m.county, 'value') else str(m.county),
                    'price_range': f"KSH {float(m.price_range):,.2f}",
                    'interest_rate': m.interest_rate,
                    'repayment_period': m.repayment_period,
                    'down_payment': f"KSH {m.down_payment:,.2f}",
                    'images': m.images if m.images else [],
                    'status': str(m.status.value) if hasattr(m.status, 'value') else str(m.status)
                })
            except Exception as enum_error:
                print(f"Enum error for mortgage {m.id}: {enum_error}")
                continue
        
        return jsonify(result), 200
    except Exception as e:
        print(f"General error: {e}")
        return jsonify([]), 200  # Return empty array instead of error

@mortgages_bp.route('/<int:mortgage_id>', methods=['GET'])
def get_mortgage(mortgage_id):
    mortgage = MortgageListing.query.get_or_404(mortgage_id)
    
    return jsonify({
        'id': mortgage.id,
        'property_title': mortgage.property_title,
        'property_type': mortgage.property_type.value,
        'address': mortgage.address,
        'county': mortgage.county.value,
        'price_range': f"KSH {float(mortgage.price_range):,.2f}",
        'interest_rate': mortgage.interest_rate,
        'repayment_period': mortgage.repayment_period,
        'down_payment': f"KSH {mortgage.down_payment:,.2f}",
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
        'bedrooms': m.bedrooms,
        'address': m.address,
        'county': m.county.value,
        'price_range': f"KSH {float(m.price_range):,.2f}",
        'interest_rate': m.interest_rate,
        'images': m.images if m.images else [],
        'status': m.status.value
    } for m in mortgages]), 200

@mortgages_bp.route('/<int:listing_id>', methods=['PATCH'])
def update_mortgage(listing_id):
    try:
        data = request.get_json()
        listing = MortgageListing.query.get_or_404(listing_id)
        
        if 'subject' in data:
            listing.property_title = data['subject']
        if 'property_type' in data:
            listing.property_type = data['property_type'].upper()
        if 'bedrooms' in data:
            listing.bedrooms = data['bedrooms']
        if 'images' in data:
            listing.images = data['images']
        if 'address' in data:
            listing.address = data['address']
        if 'county' in data:
            listing.county = data['county'].upper().replace(' ', '_')
        if 'price_range' in data:
            listing.price_range = data['price_range']
        if 'interest_rate' in data:
            listing.interest_rate = data['interest_rate']
        if 'repayment_period' in data:
            listing.repayment_period = data['repayment_period']
        if 'down_payment' in data:
            listing.down_payment = data['down_payment']
        if 'eligibility_criteria' in data:
            listing.eligibility_criteria = data['eligibility_criteria']
        
        db.session.commit()
        
        return jsonify({
            'id': listing.id,
            'message': 'Mortgage listing updated successfully'
        })
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@mortgages_bp.route('/<int:listing_id>', methods=['DELETE'])
def delete_mortgage(listing_id):
    try:
        listing = MortgageListing.query.get_or_404(listing_id)
        db.session.delete(listing)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mortgage deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400