# NetLend Backend - Mortgage Listings Routes
# This module handles all mortgage listing operations including:
# - Public mortgage browsing (for homebuyers)
# - Mortgage creation and management (for lenders)
# - Property status updates and filtering
# - CRUD operations for mortgage listings

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity  # Authentication decorators
from app import db  # Database instance
from models import Lender, MortgageListing, ListingStatus  # Database models
# from utils.cloudinary import upload_images  # Image upload service (not implemented)

# Create Blueprint for mortgage-related routes
# This allows modular organization of routes with URL prefix /api/mortgages
mortgages_bp = Blueprint('mortgages', __name__)

@mortgages_bp.route('/debug', methods=['POST'])
def debug_mortgage():
    data = request.get_json()
    print(f"Debug - Received: {data}")
    return jsonify({'received': data, 'status': 'ok'}), 200

@mortgages_bp.route('/', methods=['GET'])
def get_mortgages():
    """PUBLIC ENDPOINT: Get paginated list of active mortgage opportunities
    
    This endpoint serves the main property browsing functionality for:
    - Home page "Featured Mortgage Opportunities" section
    - Buyer dashboard "Browse Properties" section
    
    Only shows ACTIVE properties (filters out ACQUIRED and SOLD properties)
    Supports pagination for better performance with large datasets
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    
    Returns: Paginated list of mortgage listings with comprehensive property details
    """
    # Extract pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Query only ACTIVE listings (available for purchase)
    # This ensures buyers only see properties they can actually apply for
    mortgages = MortgageListing.query.filter_by(status=ListingStatus.ACTIVE).paginate(
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
@jwt_required()  # Requires valid JWT token
def create_mortgage():
    """LENDER ENDPOINT: Create new mortgage listing
    
    This endpoint allows authenticated lenders to create new property listings
    for mortgage financing. The property will be associated with the lender's account
    and appear in their "My Listings" dashboard.
    
    Authentication: Requires JWT token with lender credentials
    
    Request Body: JSON with property details including:
    - subject: Property title/name
    - property_type: apartment, bungalow, townhouse, villa
    - bedrooms: Number of bedrooms
    - address: Property address
    - county: Kenyan county location
    - price_range: Property price in KSH
    - interest_rate: Annual interest rate percentage
    - repayment_period: Loan term in years
    - down_payment: Required down payment amount
    - description: Property description (max 100 characters)
    - eligibility_criteria: Loan eligibility requirements
    - images: Array of property image URLs
    
    Returns: Success message with created listing ID
    """
    try:
        # Extract lender ID from JWT token
        # Token format: "L{lender_id}" for lenders, "U{user_id}" for legacy users
        user_id = get_jwt_identity()
        lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
        
        # Parse JSON request body
        data = request.get_json()
        print(f"Creating mortgage with data: {data}")  # Debug log for development
        
        mortgage = MortgageListing(
            property_title=data.get('subject', 'Default Title'),
            property_type=data.get('property_type', 'apartment').upper(),
            bedrooms=data.get('bedrooms', 3),
            address=data.get('address', 'Default Address'),
            county=data.get('county', 'Nairobi').upper().replace(' ', '_').replace("'", '_'),
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
                    'status': m.status.value,
                    'editable': m.status == ListingStatus.ACTIVE
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
        'status': m.status.value,
        'editable': m.status == ListingStatus.ACTIVE
    } for m in mortgages]), 200

@mortgages_bp.route('/<int:listing_id>', methods=['PATCH'])
def update_mortgage(listing_id):
    try:
        data = request.get_json()
        listing = MortgageListing.query.get_or_404(listing_id)
        
        # Prevent editing of acquired or sold houses
        if listing.status in [ListingStatus.ACQUIRED, ListingStatus.SOLD]:
            return jsonify({
                'error': 'Cannot edit house that has been acquired or sold'
            }), 403
        
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
        
        # Prevent deletion of acquired or sold houses
        if listing.status in [ListingStatus.ACQUIRED, ListingStatus.SOLD]:
            return jsonify({
                'success': False,
                'error': 'Cannot delete house that has been acquired or sold'
            }), 403
        
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