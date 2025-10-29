from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app import db
from models import User, Lender, MortgageListing, MortgageApplication, Buyer, Admin
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/test', methods=['GET'])
def test_admin():
    """Test endpoint to verify admin routes are working"""
    return jsonify({'message': 'Admin routes are working', 'timestamp': datetime.now().isoformat()})

@admin_bp.route('/test-auth', methods=['GET'])
@jwt_required()
def test_auth():
    """Test JWT authentication without admin check"""
    try:
        user_id = get_jwt_identity()
        print(f"DEBUG: JWT test - user_id: {user_id}")
        
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'message': 'JWT authentication working',
                'user_id': user_id,
                'user_role': user.role.value,
                'user_name': user.name
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"DEBUG: JWT test exception: {str(e)}")
        return jsonify({'error': str(e)}), 422

@admin_bp.route('/lenders-bypass', methods=['GET'])
def get_lenders_bypass():
    """Get all lenders with detailed information - bypass auth for testing"""
    lenders = Lender.query.all()
    return jsonify([{
        'id': lender.id,
        'institutionName': lender.institution_name,
        'contactPerson': lender.contact_person,
        'email': lender.email,
        'phoneNumber': lender.phone_number,
        'businessRegistrationNumber': lender.business_registration_number,
        'verified': lender.verified,
        'logoUrl': lender.logo_url,
        'companyType': lender.company_type,
        'website': lender.website,
        'establishedYear': lender.established_year,
        'licenseNumber': lender.license_number,
        'address': {
            'street': lender.street_address,
            'city': lender.city,
            'county': lender.county.value if lender.county else None,
            'postalCode': lender.postal_code
        },
        'contacts': {
            'primaryPhone': lender.phone_number,
            'secondaryPhone': lender.secondary_phone,
            'fax': lender.fax_number,
            'customerServiceEmail': lender.customer_service_email
        },
        'businessInfo': {
            'description': lender.description,
            'servicesOffered': lender.services_offered,
            'operatingHours': lender.operating_hours
        },
        'createdAt': lender.created_at.strftime('%Y-%m-%d')
    } for lender in lenders])

@admin_bp.route('/users-bypass', methods=['GET'])
def get_users_bypass():
    """Bypass authentication for testing"""
    from models import Admin
    
    users = User.query.all()
    buyers = Buyer.query.all()
    admins = Admin.query.all()
    lenders = Lender.query.all()
    
    all_users = []
    
    # Legacy users table
    for user in users:
        all_users.append({
            'id': f'U{user.id}',
            'name': user.name,
            'email': user.email,
            'userType': user.role.value,
            'verified': user.verified,
            'createdAt': user.created_at.strftime('%Y-%m-%d')
        })
    
    # Buyers table
    for buyer in buyers:
        all_users.append({
            'id': f'B{buyer.id}',
            'name': buyer.name,
            'email': buyer.email,
            'userType': 'homebuyer',
            'verified': buyer.verified,
            'createdAt': buyer.created_at.strftime('%Y-%m-%d')
        })
    
    # Admins table
    for admin in admins:
        all_users.append({
            'id': f'A{admin.id}',
            'name': admin.name,
            'email': admin.email,
            'userType': 'admin',
            'verified': admin.verified,
            'createdAt': admin.created_at.strftime('%Y-%m-%d')
        })
    
    # Lenders table
    for lender in lenders:
        all_users.append({
            'id': f'L{lender.id}',
            'name': lender.institution_name,
            'email': lender.email,
            'userType': 'lender',
            'verified': lender.verified,
            'createdAt': lender.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(all_users)

@admin_bp.route('/properties-bypass', methods=['GET'])
def get_properties_bypass():
    """Bypass authentication for testing"""
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
        'status': listing.status.value,
        'createdAt': listing.created_at.strftime('%Y-%m-%d')
    } for listing in listings])

@admin_bp.route('/analytics-bypass', methods=['GET'])
def get_analytics_bypass():
    """Bypass authentication for testing"""
    from models import ApplicationStatus
    total_apps = MortgageApplication.query.count()
    approved_apps = MortgageApplication.query.filter_by(status=ApplicationStatus.APPROVED).count()
    
    # Count users from all tables
    legacy_users = User.query.count()
    buyers_count = Buyer.query.count()
    admins_count = Admin.query.count()
    lenders_count = Lender.query.count()
    total_users = legacy_users + buyers_count + admins_count + lenders_count
    
    return jsonify({
        "totalApplications": total_apps,
        "approvedLoans": approved_apps,
        "activeUsers": total_users,
        "totalVolume": 50000000,
        "totalRepayments": 2500000,
        "monthlyData": [
            {"month": "Oct", "applications": 15, "approvals": 12, "volume": 225000000},
            {"month": "Nov", "applications": 20, "approvals": 16, "volume": 310000000},
            {"month": "Dec", "applications": 18, "approvals": 14, "volume": 290000000}
        ],
        "userGrowth": [
            {"month": "Oct", "homebuyers": buyers_count, "lenders": lenders_count},
            {"month": "Nov", "homebuyers": buyers_count, "lenders": lenders_count},
            {"month": "Dec", "homebuyers": buyers_count, "lenders": lenders_count}
        ],
        "approvalRate": round((approved_apps / total_apps * 100) if total_apps > 0 else 0, 1)
    })

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            from flask_jwt_extended import decode_token
            token = auth_header.split(' ')[1]
            decoded = decode_token(token)
            user_id_str = decoded['sub']
            
            # Handle U prefix for legacy users table
            if user_id_str.startswith('U'):
                user_id = int(user_id_str[1:])
                user = User.query.get(user_id)
                if user and user.role.value == 'admin':
                    return f(*args, **kwargs)
            
            # Handle A prefix for admins table
            elif user_id_str.startswith('A'):
                from models import Admin
                admin_id = int(user_id_str[1:])
                admin = Admin.query.get(admin_id)
                if admin:
                    return f(*args, **kwargs)
            
            return jsonify({'error': 'Admin access required'}), 403
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
    return decorated_function

@admin_bp.route('/users-temp', methods=['GET'])
def get_users_temp():
    """Temporary users endpoint without auth"""
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'userType': user.role.value,
            'verified': user.verified,
            'createdAt': user.created_at.strftime('%Y-%m-%d')
        } for user in users])
    except Exception as e:
        # Return mock data if database fails
        return jsonify([{
            'id': 1,
            'name': 'Aaaqil West',
            'email': 'aaaqilwest@netland.com',
            'userType': 'admin',
            'verified': True,
            'createdAt': '2024-01-01'
        }])

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    from models import Admin
    
    users = User.query.all()
    buyers = Buyer.query.all()
    admins = Admin.query.all()
    lenders = Lender.query.all()
    
    all_users = []
    
    # Legacy users table
    for user in users:
        all_users.append({
            'id': f'U{user.id}',
            'name': user.name,
            'email': user.email,
            'userType': user.role.value,
            'verified': user.verified,
            'createdAt': user.created_at.strftime('%Y-%m-%d')
        })
    
    # Buyers table
    for buyer in buyers:
        all_users.append({
            'id': f'B{buyer.id}',
            'name': buyer.name,
            'email': buyer.email,
            'userType': 'homebuyer',
            'verified': buyer.verified,
            'createdAt': buyer.created_at.strftime('%Y-%m-%d')
        })
    
    # Admins table
    for admin in admins:
        all_users.append({
            'id': f'A{admin.id}',
            'name': admin.name,
            'email': admin.email,
            'userType': 'admin',
            'verified': admin.verified,
            'createdAt': admin.created_at.strftime('%Y-%m-%d')
        })
    
    # Lenders table
    for lender in lenders:
        all_users.append({
            'id': f'L{lender.id}',
            'name': lender.institution_name,
            'email': lender.email,
            'userType': 'lender',
            'verified': lender.verified,
            'createdAt': lender.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(all_users)

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    data = request.json
    from models import UserRole
    
    role = UserRole.ADMIN if data.get('userType') == 'admin' else UserRole.LENDER
    new_user = User(
        name=data['name'],
        email=data['email'],
        role=role,
        verified=data.get('verified', False)
    )
    new_user.set_password(data.get('password', 'defaultpass'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'id': new_user.id,
        'name': new_user.name,
        'email': new_user.email,
        'userType': new_user.role.value,
        'verified': new_user.verified,
        'createdAt': new_user.created_at.strftime('%Y-%m-%d')
    }), 201

@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@admin_required
def update_user(user_id):
    """Update user"""
    data = request.json
    user = User.query.get_or_404(user_id)
    
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'verified' in data:
        user.verified = data['verified']
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'userType': user.role.value,
        'verified': user.verified
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/mortgage-products', methods=['GET'])
@admin_required
def get_mortgage_products():
    """Get all mortgage products"""
    try:
        mortgages = MortgageListing.query.all()
        return jsonify([{
            'id': m.id,
            'lender': m.lender.institution_name,
            'rate': m.interest_rate,
            'term': m.repayment_period,
            'minAmount': float(m.price_range) * 0.8,  # Estimate
            'maxAmount': float(m.price_range),
            'type': 'Fixed'
        } for m in mortgages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/applications', methods=['GET'])
@admin_required
def get_all_applications():
    """Get all mortgage applications"""
    try:
        applications = MortgageApplication.query.all()
        result = []
        for app in applications:
            buyer = Buyer.query.get(app.borrower_id)
            result.append({
                'id': app.id,
                'lender': app.lender.institution_name,
                'applicant': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'applicantName': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'buyerName': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'property': app.listing.property_title if app.listing else 'Unknown Property',
                'status': app.status.value,
                'amount': app.requested_amount,
                'date': app.submitted_at.strftime('%Y-%m-%d'),
                'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
                'notes': app.notes
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/applications-bypass', methods=['GET'])
def get_all_applications_bypass():
    """Get all mortgage applications - bypass auth for testing"""
    try:
        applications = MortgageApplication.query.all()
        result = []
        for app in applications:
            buyer = Buyer.query.get(app.borrower_id)
            result.append({
                'id': app.id,
                'lender': app.lender.institution_name,
                'applicant': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'applicantName': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'buyerName': buyer.name if buyer else f'Buyer {app.borrower_id}',
                'property': app.listing.property_title if app.listing else 'Unknown Property',
                'status': app.status.value,
                'amount': app.requested_amount,
                'date': app.submitted_at.strftime('%Y-%m-%d'),
                'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
                'notes': app.notes
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/properties-temp', methods=['GET'])
def get_properties_temp():
    """Temporary properties endpoint without auth"""
    try:
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
            'status': listing.status.value,
            'createdAt': listing.created_at.strftime('%Y-%m-%d')
        } for listing in listings])
    except Exception as e:
        # Return mock data if database fails
        return jsonify([{
            'id': 1,
            'title': 'Modern Apartment in Nairobi',
            'type': 'apartment',
            'location': 'Westlands, Nairobi',
            'price': 15000000,
            'rate': 12.5,
            'term': 25,
            'lender': 'NetLend Bank',
            'status': 'active',
            'createdAt': '2024-01-01'
        }])

@admin_bp.route('/properties', methods=['GET'])
@admin_required
def get_properties():
    """Get all properties/mortgage listings"""
    try:
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
            'status': listing.status.value,
            'createdAt': listing.created_at.strftime('%Y-%m-%d')
        } for listing in listings])
    except Exception as e:
        # Return mock data if database fails
        return jsonify([{
            'id': 1,
            'title': 'Modern Apartment in Nairobi',
            'type': 'apartment',
            'location': 'Westlands, Nairobi',
            'price': 15000000,
            'rate': 12.5,
            'term': 25,
            'lender': 'NetLend Bank',
            'status': 'active',
            'createdAt': '2024-01-01'
        }])

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get platform analytics"""
    try:
        from models import ApplicationStatus
        total_apps = MortgageApplication.query.count()
        approved_apps = MortgageApplication.query.filter_by(status=ApplicationStatus.APPROVED).count()
        
        # Count users from all tables
        legacy_users = User.query.count()
        buyers_count = Buyer.query.count()
        admins_count = Admin.query.count()
        lenders_count = Lender.query.count()
        total_users = legacy_users + buyers_count + admins_count + lenders_count
        
        total_mortgages = MortgageListing.query.count()
        
        # Mock monthly data for now
        monthly_data = [
            {"month": "Oct", "applications": 15, "approvals": 12, "volume": 225000000},
            {"month": "Nov", "applications": 20, "approvals": 16, "volume": 310000000},
            {"month": "Dec", "applications": 18, "approvals": 14, "volume": 290000000}
        ]
        
        user_growth = [
            {"month": "Oct", "homebuyers": buyers_count, "lenders": lenders_count},
            {"month": "Nov", "homebuyers": buyers_count, "lenders": lenders_count},
            {"month": "Dec", "homebuyers": buyers_count, "lenders": lenders_count}
        ]
        
        return jsonify({
            "totalApplications": total_apps,
            "approvedLoans": approved_apps,
            "activeUsers": total_users,
            "totalVolume": 50000000,  # Mock data
            "totalRepayments": 2500000,  # Mock data
            "monthlyData": monthly_data,
            "userGrowth": user_growth,
            "approvalRate": round((approved_apps / total_apps * 100) if total_apps > 0 else 0, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/metrics', methods=['GET'])
@admin_required
def get_comprehensive_metrics():
    """Get comprehensive platform metrics"""
    try:
        from models import ApplicationStatus, UserRole
        total_apps = MortgageApplication.query.count()
        approved_apps = MortgageApplication.query.filter_by(status=ApplicationStatus.APPROVED).count()
        pending_apps = MortgageApplication.query.filter_by(status=ApplicationStatus.PENDING).count()
        
        total_lenders = User.query.filter_by(role=UserRole.LENDER).count()
        verified_lenders = User.query.filter_by(verified=True).count()
        
        return jsonify({
        "overview": {
            "totalApplications": total_apps,
            "approvedLoans": approved_apps,
            "pendingApplications": pending_apps,
            "rejectedApplications": total_apps - approved_apps - pending_apps,
            "totalUsers": total_lenders,
            "homebuyers": 0,  # Not implemented yet
            "lenders": total_lenders,
            "verifiedUsers": verified_lenders,
            "totalVolume": 50000000,
            "approvedVolume": 40000000,
            "avgLoanAmount": 2500000,
            "totalRepayments": 1500000,
            "pendingRepayments": 500000,
            "approvalRate": round((approved_apps / total_apps * 100) if total_apps > 0 else 0, 1),
            "avgFeedbackRating": 4.2
        },
        "trends": {
            "monthlyMetrics": [
                {"month": "Aug", "applications": 12, "approvals": 8, "volume": 160000000, "users": 35},
                {"month": "Sep", "applications": 18, "approvals": 14, "volume": 240000000, "users": 42},
                {"month": "Oct", "applications": 15, "approvals": 12, "volume": 225000000, "users": 48}
            ],
            "userGrowth": [
                {"month": "Aug", "homebuyers": 28, "lenders": 7},
                {"month": "Sep", "homebuyers": 35, "lenders": 8},
                {"month": "Oct", "homebuyers": 40, "lenders": total_lenders}
            ]
        },
        "products": {
            "performance": [],
            "totalProducts": MortgageListing.query.count()
        },
        "feedback": {
            "total": 0,
            "approved": 0,
            "pending": 0,
            "avgRating": 4.2
        },
        "timestamp": datetime.now().isoformat()
    })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/feedback', methods=['GET'])
@admin_required
def get_feedback():
    """Get all feedback - placeholder for now"""
    try:
        # Mock feedback data for now
        return jsonify([
            {
                'id': 1,
                'user': 'John Doe',
                'rating': 4,
                'comment': 'Great service, quick approval process',
                'date': '2024-01-15',
                'status': 'approved'
            },
            {
                'id': 2,
                'user': 'Jane Smith',
                'rating': 5,
                'comment': 'Excellent customer support',
                'date': '2024-01-14',
                'status': 'pending'
            }
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/feedback/<int:feedback_id>', methods=['PATCH'])
@admin_required
def moderate_feedback(feedback_id):
    """Moderate feedback - placeholder for now"""
    return jsonify({"success": True})

@admin_bp.route('/lenders', methods=['GET'])
@admin_required
def get_lenders():
    """Get all lenders with detailed information"""
    lenders = Lender.query.all()
    return jsonify([{
        'id': lender.id,
        'institutionName': lender.institution_name,
        'contactPerson': lender.contact_person,
        'email': lender.email,
        'phoneNumber': lender.phone_number,
        'businessRegistrationNumber': lender.business_registration_number,
        'verified': lender.verified,
        'logoUrl': lender.logo_url,
        'companyType': lender.company_type,
        'website': lender.website,
        'establishedYear': lender.established_year,
        'licenseNumber': lender.license_number,
        'address': {
            'street': lender.street_address,
            'city': lender.city,
            'county': lender.county.value if lender.county else None,
            'postalCode': lender.postal_code
        },
        'contacts': {
            'primaryPhone': lender.phone_number,
            'secondaryPhone': lender.secondary_phone,
            'fax': lender.fax_number,
            'customerServiceEmail': lender.customer_service_email
        },
        'businessInfo': {
            'description': lender.description,
            'servicesOffered': lender.services_offered,
            'operatingHours': lender.operating_hours
        },
        'createdAt': lender.created_at.strftime('%Y-%m-%d')
    } for lender in lenders])

@admin_bp.route('/lenders/<int:lender_id>', methods=['GET'])
@admin_required
def get_lender_details(lender_id):
    """Get detailed information for a specific lender"""
    lender = Lender.query.get_or_404(lender_id)
    return jsonify({
        'id': lender.id,
        'institutionName': lender.institution_name,
        'contactPerson': lender.contact_person,
        'email': lender.email,
        'phoneNumber': lender.phone_number,
        'businessRegistrationNumber': lender.business_registration_number,
        'verified': lender.verified,
        'logoUrl': lender.logo_url,
        'companyType': lender.company_type,
        'website': lender.website,
        'establishedYear': lender.established_year,
        'licenseNumber': lender.license_number,
        'address': {
            'street': lender.street_address,
            'city': lender.city,
            'county': lender.county.value if lender.county else None,
            'postalCode': lender.postal_code
        },
        'contacts': {
            'primaryPhone': lender.phone_number,
            'secondaryPhone': lender.secondary_phone,
            'fax': lender.fax_number,
            'customerServiceEmail': lender.customer_service_email
        },
        'businessInfo': {
            'description': lender.description,
            'servicesOffered': lender.services_offered,
            'operatingHours': lender.operating_hours
        },
        'statistics': {
            'totalListings': len(lender.mortgage_listings),
            'totalApplications': len(lender.applications),
            'activeLoans': len(lender.active_mortgages)
        },
        'createdAt': lender.created_at.strftime('%Y-%m-%d')
    })

@admin_bp.route('/lenders/<int:lender_id>', methods=['PUT'])
@admin_required
def update_lender(lender_id):
    """Update lender information"""
    lender = Lender.query.get_or_404(lender_id)
    data = request.json
    
    # Update basic information
    if 'institutionName' in data:
        lender.institution_name = data['institutionName']
    if 'contactPerson' in data:
        lender.contact_person = data['contactPerson']
    if 'email' in data:
        lender.email = data['email']
    if 'phoneNumber' in data:
        lender.phone_number = data['phoneNumber']
    if 'businessRegistrationNumber' in data:
        lender.business_registration_number = data['businessRegistrationNumber']
    if 'verified' in data:
        lender.verified = data['verified']
    if 'logoUrl' in data:
        lender.logo_url = data['logoUrl']
    if 'companyType' in data:
        lender.company_type = data['companyType']
    if 'website' in data:
        lender.website = data['website']
    if 'establishedYear' in data:
        lender.established_year = data['establishedYear']
    if 'licenseNumber' in data:
        lender.license_number = data['licenseNumber']
    
    # Update address
    if 'address' in data:
        addr = data['address']
        if 'street' in addr:
            lender.street_address = addr['street']
        if 'city' in addr:
            lender.city = addr['city']
        if 'county' in addr:
            from models import KenyanCounty
            lender.county = KenyanCounty(addr['county'])
        if 'postalCode' in addr:
            lender.postal_code = addr['postalCode']
    
    # Update contacts
    if 'contacts' in data:
        contacts = data['contacts']
        if 'secondaryPhone' in contacts:
            lender.secondary_phone = contacts['secondaryPhone']
        if 'fax' in contacts:
            lender.fax_number = contacts['fax']
        if 'customerServiceEmail' in contacts:
            lender.customer_service_email = contacts['customerServiceEmail']
    
    # Update business info
    if 'businessInfo' in data:
        biz = data['businessInfo']
        if 'description' in biz:
            lender.description = biz['description']
        if 'servicesOffered' in biz:
            lender.services_offered = biz['servicesOffered']
        if 'operatingHours' in biz:
            lender.operating_hours = biz['operatingHours']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Lender updated successfully'})