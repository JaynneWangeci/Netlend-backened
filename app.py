# NetLend Backend - Main Application File
# This file sets up the Flask application, configures extensions, and defines core authentication routes

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # ORM for database operations
from flask_migrate import Migrate  # Database schema versioning
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  # JWT authentication
from flask_cors import CORS  # Cross-origin resource sharing for frontend communication
from flask_mail import Mail  # Email functionality (configured but not actively used)
from functools import wraps  # Decorator utilities
from datetime import datetime, timedelta  # Date/time handling
from config import Config  # Application configuration

# Initialize Flask extensions - these will be configured when the app is created
db = SQLAlchemy()  # Database ORM instance
migrate = Migrate()  # Database migration manager
jwt = JWTManager()  # JWT token manager
mail = Mail()  # Email service manager

def create_app():
    """Application factory pattern - creates and configures Flask application instance"""
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from config.py
    
    # Initialize extensions with the app instance
    # This pattern allows for multiple app instances and easier testing
    db.init_app(app)  # Configure SQLAlchemy with app
    migrate.init_app(app, db)  # Set up database migrations
    jwt.init_app(app)  # Configure JWT authentication
    mail.init_app(app)  # Set up email service

    # Configure CORS (Cross-Origin Resource Sharing)
    # This allows the frontend (React/Vue) to communicate with the backend API
    # from different ports/domains during development
    CORS(
        app,
        origins=[
<<<<<<< HEAD
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'http://localhost:3000',
            'http://localhost:3001',
            'https://*.onrender.com',
            'https://*.netlify.app',
            'https://*.vercel.app'
=======
            'http://localhost:5173',  # Vite dev server (React/Vue)
            'http://127.0.0.1:5173',  # Alternative localhost format
            'http://localhost:3000',  # Create React App default port
            'http://localhost:3001'   # Alternative React port
>>>>>>> 9bf88590d110efe18082e2aeacc112f4363ae20c
        ],
        supports_credentials=True,  # Allow cookies and auth headers
        allow_headers=['Content-Type', 'Authorization', 'Accept'],  # Permitted request headers
        methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTIONS'],  # Allowed HTTP methods
        expose_headers=['Content-Type', 'Authorization']  # Headers exposed to frontend
    )

    # Import and register blueprints
    try:
        from routes.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        print("✅ Admin routes registered")
    except Exception as e:
        print(f"❌ Failed to register admin routes: {e}")
    
    try:
        from routes.mortgages import mortgages_bp
        app.register_blueprint(mortgages_bp, url_prefix='/api/mortgages')
        print("✅ Mortgage routes registered")
    except Exception as e:
        print(f"❌ Failed to register mortgage routes: {e}")
    
    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("✅ Auth routes registered")
    except Exception as e:
        print(f"❌ Failed to register auth routes: {e}")
    
    try:
        from routes.homebuyer import homebuyer_bp
        app.register_blueprint(homebuyer_bp, url_prefix='/api/homebuyer')
        print("✅ Homebuyer routes registered")
    except Exception as e:
        print(f"❌ Failed to register homebuyer routes: {e}")
    
    try:
        from routes.lender import lender_bp
        app.register_blueprint(lender_bp, url_prefix='/api/lender')
        print("✅ Lender routes registered")
    except Exception as e:
        print(f"❌ Failed to register lender routes: {e}")
    
    try:
        from routes.payments import payments_bp
        app.register_blueprint(payments_bp, url_prefix='/api/payments')
        print("✅ Payment routes registered")
    except Exception as e:
        print(f"❌ Failed to register payment routes: {e}")
    
    # Role-based middleware
    def token_required(allowed_roles=None):
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                user_id = get_jwt_identity()
                from models import User
                user = User.query.get_or_404(user_id)
                
                user_role = user.role.value
                
                if allowed_roles and user_role not in allowed_roles:
                    return jsonify({'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'}), 403
                
                request.current_user = {'user_id': user.id, 'email': user.email, 'role': user_role}
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # Auth endpoints
    # AUTHENTICATION ENDPOINTS
    # These routes handle user login, registration, and token validation
    # The system supports 4 user types: Buyers (B), Lenders (L), Admins (A), and Legacy Users (U)
    
    @app.route('/api/login', methods=['POST'])
    def login():
        """Universal login endpoint that checks all user tables and returns appropriate JWT token"""
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Basic validation
        if not email:
            return jsonify({
                "success": False,
                "modal": {
                    "type": "error",
                    "title": "Login Failed",
                    "message": "Email is required to login."
                }
            }), 400
        
        # Import models here to avoid circular imports
        from models import User, Lender, Buyer, Admin
        
        # Check User table (legacy admin users)
        # This table contains the original admin users before separate tables were created
        user = User.query.filter_by(email=email).first()
        if user and password and user.check_password(password):
            # Create JWT token with 'U' prefix to identify legacy users
            token = create_access_token(identity=f"U{user.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "userType": user.role.value,  # admin, lender, or homebuyer
                    "verified": user.verified
                },
                "token": token  # JWT token for subsequent API calls
            })
        
        # Check Buyer table
        buyer = Buyer.query.filter_by(email=email).first()
        if buyer and password and buyer.check_password(password):
            token = create_access_token(identity=f"B{buyer.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": buyer.id,
                    "name": buyer.name,
                    "email": buyer.email,
                    "userType": "homebuyer",
                    "verified": buyer.verified
                },
                "token": token
            })
        
        # Check Admin table
        admin = Admin.query.filter_by(email=email).first()
        if admin and password and admin.check_password(password):
            token = create_access_token(identity=f"A{admin.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "userType": "admin",
                    "verified": admin.verified
                },
                "token": token
            })
        
        # Check Lender table
        lender = Lender.query.filter_by(email=email).first()
        if lender and password and lender.check_password(password):
            token = create_access_token(identity=f"L{lender.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": lender.id,
                    "name": lender.institution_name,
                    "email": lender.email,
                    "userType": "lender",
                    "verified": lender.verified
                },
                "token": token
            })
        
        return jsonify({
            "success": False,
            "modal": {
                "type": "error",
                "title": "Login Failed",
                "message": "Invalid email or password. Please try again."
            }
        }), 401

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        
        name = data.get('name') or data.get('institution_name')
        email = data.get('email')
        user_type = data.get('userType', 'lender')
        
        if not name or not email:
            return jsonify({
                "success": False,
                "modal": {
                    "type": "error",
                    "title": "Registration Failed",
                    "message": "Name and email are required for registration."
                }
            }), 400
        
        from models import User, UserRole, Lender, Buyer, Admin
        
        # Check if email exists in any table
        if (User.query.filter_by(email=email).first() or 
            Lender.query.filter_by(email=email).first() or
            Buyer.query.filter_by(email=email).first() or
            Admin.query.filter_by(email=email).first()):
            return jsonify({
                "success": False,
                "modal": {
                    "type": "warning",
                    "title": "Registration Failed",
                    "message": "An account with this email already exists. Please login instead."
                }
            }), 409
        
        if user_type in ['homebuyer', 'buyer']:
            # Create in Buyer table
            buyer = Buyer(
                name=name,
                email=email,
                verified=True
            )
            buyer.set_password(data.get('password', 'defaultpass'))
            db.session.add(buyer)
            db.session.commit()
            
            token = create_access_token(identity=f"B{buyer.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": buyer.id,
                    "name": buyer.name,
                    "email": buyer.email,
                    "userType": "homebuyer",
                    "verified": buyer.verified
                },
                "token": token
            }), 201
        elif user_type == 'admin':
            # Create in Admin table
            admin = Admin(
                name=name,
                email=email,
                verified=True
            )
            admin.set_password(data.get('password', 'defaultpass'))
            db.session.add(admin)
            db.session.commit()
            
            token = create_access_token(identity=f"A{admin.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "userType": "admin",
                    "verified": admin.verified
                },
                "token": token
            }), 201
        else:
            # Create in Lender table
            lender = Lender(
                email=email,
                institution_name=name,
                contact_person=name,
                verified=True
            )
            lender.set_password(data.get('password', 'defaultpass'))
            db.session.add(lender)
            db.session.commit()
            
            token = create_access_token(identity=f"L{lender.id}")
            return jsonify({
                "success": True,
                "user": {
                    "id": lender.id,
                    "name": lender.institution_name,
                    "email": lender.email,
                    "userType": "lender",
                    "verified": lender.verified
                },
                "token": token
            }), 201

    @app.route('/api/validate-token', methods=['POST'])
    @token_required()
    def validate_token():
        user_info = request.current_user
        return jsonify({
            "valid": True,
            "user": {
                "id": user_info['user_id'],
                "email": user_info['email'],
                "role": user_info['role']
            }
        })

    @app.route('/api/lenders', methods=['GET'])
    def get_all_lenders():
        from models import Lender
        lenders = Lender.query.all()
        return jsonify([{
            'id': lender.id,
            'name': lender.institution_name,
            'email': lender.email,
            'verified': lender.verified,
            'createdAt': lender.created_at.strftime('%Y-%m-%d')
        } for lender in lenders])

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "message": "NetLend API is running"})
    
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response
    
    @app.route('/api/debug/admin', methods=['GET'])
    def debug_admin():
        """Debug endpoint to test admin functionality"""
        return jsonify({
            "message": "Admin debug endpoint working",
            "timestamp": datetime.now().isoformat(),
            "routes_available": [
                "/api/admin/test",
                "/api/admin/users", 
                "/api/admin/properties",
                "/api/admin/analytics"
            ]
        })
    
    @app.route('/api/loan-products', methods=['GET'])
    def get_loan_products():
        from models import MortgageListing
        listings = MortgageListing.query.all()
        return jsonify([{
            'id': listing.id,
            'lender': listing.lender.institution_name,
            'rate': listing.interest_rate,
            'term': listing.repayment_period,
            'maxAmount': float(listing.price_range)
        } for listing in listings])
    
    @app.route('/api/applications', methods=['POST'])
    @jwt_required()
    def create_application():
        try:
            user_id = get_jwt_identity()
            data = request.json
            
            print(f'Application data: {data}')  # Debug log
            print(f'User ID: {user_id}')  # Debug log
            
            from models import MortgageApplication
            
            # Get property details
            listing_id = data.get('id')
            loan_amount = data.get('price', 0) * 0.8  # 80% of property price
            repayment_years = data.get('term', 25)
            
            # Get lender_id from the listing
            from models import MortgageListing
            listing = MortgageListing.query.get(listing_id)
            if not listing:
                return jsonify({'error': 'Property not found'}), 404
            
            application = MortgageApplication(
                borrower_id=int(user_id[1:]) if user_id.startswith('B') else int(user_id),
                lender_id=listing.lender_id,
                listing_id=listing_id,
                requested_amount=loan_amount,
                repayment_years=repayment_years
            )
            
            db.session.add(application)
            db.session.commit()
            
            return jsonify({'id': application.id, 'status': 'submitted'}), 201
        except Exception as e:
            print(f'Application error: {e}')
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/docs')
    def swagger_docs():
        return '''<!DOCTYPE html>
        <html><head><title>NetLend API Documentation</title></head>
        <body><h1>NetLend API Documentation</h1>
        <h2>Authentication Endpoints</h2>
        <p>POST /api/login - User authentication</p>
        <p>POST /api/register - User registration</p>
        <p>POST /api/validate-token - Validate JWT token</p>
        <h2>Admin Endpoints</h2>
        <p>GET /api/admin/users - Get all users</p>
        <p>POST /api/admin/users - Create user</p>
        <p>GET /api/admin/analytics - Get analytics</p>
        <p>GET /api/admin/metrics - Get comprehensive metrics</p>
        <h2>Lender Endpoints</h2>
        <p>POST /api/mortgages/ - Create mortgage listing</p>
        <p>GET /api/lender/{id}/mortgages - Get lender mortgages</p>
        <p>GET /api/lenders - Get all lenders</p>
        </body></html>'''

    return app

import os

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 NetLend Backend Starting on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
