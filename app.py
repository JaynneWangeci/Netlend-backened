from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime, timedelta

try:
    import jwt
except ImportError:
    print("Warning: PyJWT not installed. Install with: pip install PyJWT")
    jwt = None

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'netland-secret-key-2024')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=24)

# Mock data
users = [
    {"id": 1, "name": "John Homebuyer", "email": "user@example.com", "userType": "homebuyer", "verified": True, "createdAt": "2024-01-01"},
    {"id": 2, "name": "Pending Lender", "email": "newlender@bank.com", "userType": "lender", "verified": False, "createdAt": "2024-01-15"},
    {"id": 3, "name": "Admin User", "email": "admin@netland.com", "userType": "admin", "verified": True, "createdAt": "2024-01-01"}
]

mortgage_products = [
    {"id": 1, "lender": "Equity Bank Kenya", "rate": 12.5, "term": 30, "minAmount": 5000000, "maxAmount": 50000000, "type": "Fixed"},
    {"id": 2, "lender": "KCB Bank", "rate": 11.8, "term": 25, "minAmount": 3000000, "maxAmount": 30000000, "type": "Fixed"}
]

applications = [
    {"id": 1, "lender": "Equity Bank Kenya", "applicant": "user@example.com", "status": "pending", "amount": 15000000, "date": "2024-01-15"},
    {"id": 2, "lender": "KCB Bank", "applicant": "user@example.com", "status": "approved", "amount": 12000000, "date": "2024-01-10"}
]

repayments = [
    {"id": 1, "applicationId": 2, "amount": 75000, "date": "2024-01-15", "status": "paid"},
    {"id": 2, "applicationId": 2, "amount": 75000, "date": "2024-02-15", "status": "pending"}
]

feedback = [
    {"id": 1, "userId": 1, "message": "Great platform!", "rating": 5, "status": "approved", "date": "2024-01-20"},
    {"id": 2, "userId": 2, "message": "Needs improvement", "rating": 3, "status": "pending", "date": "2024-01-22"}
]

# JWT Helper Functions
def generate_token(user):
    """Generate JWT token for user"""
    if not jwt:
        return f"mock-token-{user['userType']}-{user['id']}"
    
    payload = {
        'user_id': user['id'],
        'email': user['email'],
        'role': user['userType'],
        'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify and decode JWT token"""
    if not jwt:
        # Mock verification for development
        if token.startswith('mock-token-'):
            parts = token.split('-')
            return {'role': parts[2], 'user_id': int(parts[3])}
        return None
    
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Role-based middleware
def token_required(allowed_roles=None):
    """Decorator for JWT token validation with role checking"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                except IndexError:
                    return jsonify({'error': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'error': 'Token missing'}), 401
            
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check role permissions
            if allowed_roles and payload.get('role') not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'}), 403
            
            # Add user info to request context
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Convenience decorators
def admin_required(f):
    return token_required(['admin'])(f)

def lender_required(f):
    return token_required(['admin', 'lender'])(f)

def user_required(f):
    return token_required(['admin', 'lender', 'homebuyer'])(f)

# Auth Endpoints
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"success": False, "error": "Email required"}), 400
    
    user = next((u for u in users if u['email'] == email), None)
    if user:
        token = generate_token(user)
        return jsonify({
            "success": True, 
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "userType": user['userType'],
                "verified": user['verified']
            }, 
            "token": token
        })
    return jsonify({"success": False, "error": "User not found"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'email', 'userType']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"{field} is required"}), 400
    
    # Check if user already exists
    if any(u['email'] == data['email'] for u in users):
        return jsonify({"success": False, "error": "User already exists"}), 409
    
    new_user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data['email'],
        "userType": data['userType'],
        "verified": data['userType'] == 'admin',
        "createdAt": datetime.now().strftime('%Y-%m-%d')
    }
    users.append(new_user)
    
    token = generate_token(new_user)
    return jsonify({
        "success": True, 
        "user": {
            "id": new_user['id'],
            "name": new_user['name'],
            "email": new_user['email'],
            "userType": new_user['userType'],
            "verified": new_user['verified']
        }, 
        "token": token
    }), 201

@app.route('/api/validate-token', methods=['POST'])
@user_required
def validate_token():
    """Validate JWT token and return user info"""
    user_info = request.current_user
    return jsonify({
        "valid": True,
        "user": {
            "id": user_info['user_id'],
            "email": user_info.get('email', ''),
            "role": user_info['role']
        }
    })

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    return jsonify(users)

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    new_user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data['email'],
        "userType": data['userType'],
        "verified": data.get('verified', False),
        "createdAt": datetime.now().strftime('%Y-%m-%d')
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    data = request.json
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        user.update(data)
        send_notification(user['email'], 'Account Updated', f'Your account has been updated by an administrator.')
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    global users
    users = [u for u in users if u['id'] != user_id]
    return jsonify({"success": True})

@app.route('/api/admin/mortgage-products', methods=['GET'])
@admin_required
def get_mortgage_products():
    return jsonify(mortgage_products)

@app.route('/api/admin/applications', methods=['GET'])
@admin_required
def get_all_applications():
    return jsonify(applications)

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def get_analytics():
    total_apps = len(applications)
    approved_apps = len([a for a in applications if a['status'] == 'approved'])
    total_users = len([u for u in users if u['userType'] != 'admin'])
    total_volume = sum(a['amount'] for a in applications)
    total_repayments = sum(r['amount'] for r in repayments if r['status'] == 'paid')
    
    monthly_data = [
        {"month": "Jan", "applications": 15, "approvals": 12, "volume": 225000000},
        {"month": "Feb", "applications": 20, "approvals": 16, "volume": 310000000},
        {"month": "Mar", "applications": 18, "approvals": 14, "volume": 290000000}
    ]
    
    user_growth = [
        {"month": "Jan", "homebuyers": 45, "lenders": 8},
        {"month": "Feb", "homebuyers": 62, "lenders": 12},
        {"month": "Mar", "homebuyers": 78, "lenders": 15}
    ]
    
    return jsonify({
        "totalApplications": total_apps,
        "approvedLoans": approved_apps,
        "activeUsers": total_users,
        "totalVolume": total_volume,
        "totalRepayments": total_repayments,
        "monthlyData": monthly_data,
        "userGrowth": user_growth,
        "approvalRate": round((approved_apps / total_apps * 100) if total_apps > 0 else 0, 1)
    })

@app.route('/api/admin/feedback', methods=['GET'])
@admin_required
def get_feedback():
    return jsonify(feedback)

@app.route('/api/admin/feedback/<int:feedback_id>', methods=['PUT'])
@admin_required
def moderate_feedback(feedback_id):
    data = request.json
    fb = next((f for f in feedback if f['id'] == feedback_id), None)
    if fb:
        fb['status'] = data.get('status', fb['status'])
        return jsonify(fb)
    return jsonify({"error": "Feedback not found"}), 404

@app.route('/api/admin/metrics', methods=['GET'])
@admin_required
def get_comprehensive_metrics():
    """Get comprehensive platform metrics for dashboard analytics"""
    
    # Calculate core metrics
    total_apps = len(applications)
    approved_apps = len([a for a in applications if a['status'] == 'approved'])
    pending_apps = len([a for a in applications if a['status'] == 'pending'])
    rejected_apps = total_apps - approved_apps - pending_apps
    
    homebuyers = len([u for u in users if u['userType'] == 'homebuyer'])
    lenders = len([u for u in users if u['userType'] == 'lender'])
    verified_users = len([u for u in users if u['verified'] and u['userType'] != 'admin'])
    
    total_volume = sum(a['amount'] for a in applications)
    approved_volume = sum(a['amount'] for a in applications if a['status'] == 'approved')
    avg_loan_amount = approved_volume / approved_apps if approved_apps > 0 else 0
    
    total_repayments = sum(r['amount'] for r in repayments if r['status'] == 'paid')
    pending_repayments = sum(r['amount'] for r in repayments if r['status'] == 'pending')
    
    # Performance metrics
    approval_rate = round((approved_apps / total_apps * 100) if total_apps > 0 else 0, 1)
    avg_feedback_rating = sum(f['rating'] for f in feedback) / len(feedback) if feedback else 0
    
    # Time-based data (last 6 months)
    monthly_metrics = [
        {"month": "Aug", "applications": 12, "approvals": 8, "volume": 160000000, "users": 35},
        {"month": "Sep", "applications": 18, "approvals": 14, "volume": 240000000, "users": 42},
        {"month": "Oct", "applications": 15, "approvals": 12, "volume": 225000000, "users": 48},
        {"month": "Nov", "applications": 22, "approvals": 18, "volume": 310000000, "users": 55},
        {"month": "Dec", "applications": 20, "approvals": 16, "volume": 290000000, "users": 63},
        {"month": "Jan", "applications": 25, "approvals": 20, "volume": 360000000, "users": 72}
    ]
    
    # User growth by type
    user_growth_data = [
        {"month": "Aug", "homebuyers": 28, "lenders": 7},
        {"month": "Sep", "homebuyers": 35, "lenders": 7},
        {"month": "Oct", "homebuyers": 40, "lenders": 8},
        {"month": "Nov", "homebuyers": 47, "lenders": 8},
        {"month": "Dec", "homebuyers": 55, "lenders": 8},
        {"month": "Jan", "homebuyers": 62, "lenders": 10}
    ]
    
    # Product performance
    product_metrics = []
    for product in mortgage_products:
        product_apps = [a for a in applications if a['lender'] == product['lender']]
        product_metrics.append({
            "lender": product['lender'],
            "applications": len(product_apps),
            "approvals": len([a for a in product_apps if a['status'] == 'approved']),
            "rate": product['rate'],
            "volume": sum(a['amount'] for a in product_apps)
        })
    
    return jsonify({
        "overview": {
            "totalApplications": total_apps,
            "approvedLoans": approved_apps,
            "pendingApplications": pending_apps,
            "rejectedApplications": rejected_apps,
            "totalUsers": homebuyers + lenders,
            "homebuyers": homebuyers,
            "lenders": lenders,
            "verifiedUsers": verified_users,
            "totalVolume": total_volume,
            "approvedVolume": approved_volume,
            "avgLoanAmount": round(avg_loan_amount, 2),
            "totalRepayments": total_repayments,
            "pendingRepayments": pending_repayments,
            "approvalRate": approval_rate,
            "avgFeedbackRating": round(avg_feedback_rating, 1)
        },
        "trends": {
            "monthlyMetrics": monthly_metrics,
            "userGrowth": user_growth_data
        },
        "products": {
            "performance": product_metrics,
            "totalProducts": len(mortgage_products)
        },
        "feedback": {
            "total": len(feedback),
            "approved": len([f for f in feedback if f['status'] == 'approved']),
            "pending": len([f for f in feedback if f['status'] == 'pending']),
            "avgRating": round(avg_feedback_rating, 1)
        },
        "timestamp": datetime.now().isoformat()
    })

def send_notification(email, subject, message="System notification"):
    """Send email notification using SendGrid (mock implementation)"""
    # Mock SendGrid integration - replace with actual SendGrid API
    try:
        print(f"📧 SendGrid Email: {email} | Subject: {subject} | Message: {message}")
        # In production, use SendGrid API:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # mail = Mail(from_email='admin@netland.com', to_emails=email, subject=subject, html_content=message)
        # response = sg.send(mail)
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

@app.route('/docs')
def swagger_docs():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Netland API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .method { font-weight: bold; color: #2563eb; }
            .path { font-family: monospace; background: #f3f4f6; padding: 2px 6px; }
        </style>
    </head>
    <body>
        <h1>Netland Admin API Documentation</h1>
        
        <h2>Authentication Endpoints</h2>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/login</span><br>
            <strong>Description:</strong> User authentication<br>
            <strong>Body:</strong> {"email": "string", "userType": "admin|lender|homebuyer"}
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/register</span><br>
            <strong>Description:</strong> User registration<br>
            <strong>Body:</strong> {"name": "string", "email": "string", "userType": "admin|lender|homebuyer"}
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/validate-token</span><br>
            <strong>Description:</strong> Validate JWT token<br>
            <strong>Headers:</strong> Authorization: Bearer {token}
        </div>
        
        <h2>Admin User Management (Requires admin-token)</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/users</span><br>
            <strong>Description:</strong> Get all users
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/api/admin/users</span><br>
            <strong>Description:</strong> Create new user<br>
            <strong>Body:</strong> {"name": "string", "email": "string", "userType": "string", "verified": boolean}
        </div>
        <div class="endpoint">
            <span class="method">PUT</span> <span class="path">/api/admin/users/{id}</span><br>
            <strong>Description:</strong> Update user
        </div>
        <div class="endpoint">
            <span class="method">DELETE</span> <span class="path">/api/admin/users/{id}</span><br>
            <strong>Description:</strong> Delete user
        </div>
        
        <h2>Admin Mortgage Oversight (Requires admin-token)</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/mortgage-products</span><br>
            <strong>Description:</strong> Get all mortgage products
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/applications</span><br>
            <strong>Description:</strong> Get all mortgage applications
        </div>
        
        <h2>Admin Analytics (Requires admin-token)</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/analytics</span><br>
            <strong>Description:</strong> Get platform analytics and metrics
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/metrics</span><br>
            <strong>Description:</strong> Get comprehensive platform metrics with detailed breakdowns
        </div>
        
        <h2>Admin Feedback Management (Requires admin-token)</h2>
        <div class="endpoint">
            <span class="method">GET</span> <span class="path">/api/admin/feedback</span><br>
            <strong>Description:</strong> Get all user feedback
        </div>
        <div class="endpoint">
            <span class="method">PUT</span> <span class="path">/api/admin/feedback/{id}</span><br>
            <strong>Description:</strong> Moderate feedback<br>
            <strong>Body:</strong> {"status": "approved|rejected|pending"}
        </div>
        
        <p><strong>Authentication:</strong> Include 'Authorization: Bearer {jwt_token}' header for protected endpoints</p>
        <p><strong>Roles:</strong> admin (full access), lender (mortgage management), homebuyer (applications)</p>
    </body>
    </html>
    '''

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Netland API is running"})

if __name__ == '__main__':
    print("🚀 Netland Backend Starting...")
    print("📍 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("💚 Health: http://localhost:5000/health")
    app.run(debug=True, port=5000, host='0.0.0.0')