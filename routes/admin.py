from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app import db
from models import Lender, MortgageListing, MortgageApplication
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = Lender.query.get_or_404(user_id)
        # For now, check if user email contains 'admin' - replace with proper admin role check
        if 'admin' not in user.email.lower():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    lenders = Lender.query.all()
    return jsonify([{
        'id': lender.id,
        'name': lender.institution_name,
        'email': lender.email,
        'userType': 'lender',
        'verified': lender.verified,
        'createdAt': lender.created_at.strftime('%Y-%m-%d')
    } for lender in lenders])

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    data = request.json
    
    new_lender = Lender(
        institution_name=data['name'],
        contact_person=data.get('contact_person', data['name']),
        email=data['email'],
        verified=data.get('verified', False)
    )
    new_lender.set_password(data.get('password', 'defaultpass'))
    
    db.session.add(new_lender)
    db.session.commit()
    
    return jsonify({
        'id': new_lender.id,
        'name': new_lender.institution_name,
        'email': new_lender.email,
        'userType': 'lender',
        'verified': new_lender.verified,
        'createdAt': new_lender.created_at.strftime('%Y-%m-%d')
    }), 201

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user"""
    data = request.json
    lender = Lender.query.get_or_404(user_id)
    
    if 'name' in data:
        lender.institution_name = data['name']
    if 'email' in data:
        lender.email = data['email']
    if 'verified' in data:
        lender.verified = data['verified']
    
    db.session.commit()
    
    return jsonify({
        'id': lender.id,
        'name': lender.institution_name,
        'email': lender.email,
        'userType': 'lender',
        'verified': lender.verified
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    lender = Lender.query.get_or_404(user_id)
    db.session.delete(lender)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/mortgage-products', methods=['GET'])
@admin_required
def get_mortgage_products():
    """Get all mortgage products"""
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

@admin_bp.route('/applications', methods=['GET'])
@admin_required
def get_all_applications():
    """Get all mortgage applications"""
    applications = MortgageApplication.query.all()
    return jsonify([{
        'id': app.id,
        'lender': app.lender.institution_name,
        'applicant': f'borrower_{app.borrower_id}',
        'status': app.status.value,
        'amount': app.requested_amount,
        'date': app.submitted_at.strftime('%Y-%m-%d')
    } for app in applications])

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get platform analytics"""
    total_apps = MortgageApplication.query.count()
    approved_apps = MortgageApplication.query.filter_by(status='approved').count()
    total_users = Lender.query.count()
    total_mortgages = MortgageListing.query.count()
    
    # Mock monthly data for now
    monthly_data = [
        {"month": "Oct", "applications": 15, "approvals": 12, "volume": 225000000},
        {"month": "Nov", "applications": 20, "approvals": 16, "volume": 310000000},
        {"month": "Dec", "applications": 18, "approvals": 14, "volume": 290000000}
    ]
    
    user_growth = [
        {"month": "Oct", "homebuyers": 45, "lenders": total_users},
        {"month": "Nov", "homebuyers": 62, "lenders": total_users},
        {"month": "Dec", "homebuyers": 78, "lenders": total_users}
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

@admin_bp.route('/metrics', methods=['GET'])
@admin_required
def get_comprehensive_metrics():
    """Get comprehensive platform metrics"""
    total_apps = MortgageApplication.query.count()
    approved_apps = MortgageApplication.query.filter_by(status='approved').count()
    pending_apps = MortgageApplication.query.filter_by(status='pending').count()
    
    total_lenders = Lender.query.count()
    verified_lenders = Lender.query.filter_by(verified=True).count()
    
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

@admin_bp.route('/feedback', methods=['GET'])
@admin_required
def get_feedback():
    """Get all feedback - placeholder for now"""
    return jsonify([])

@admin_bp.route('/feedback/<int:feedback_id>', methods=['PUT'])
@admin_required
def moderate_feedback(feedback_id):
    """Moderate feedback - placeholder for now"""
    return jsonify({"success": True})