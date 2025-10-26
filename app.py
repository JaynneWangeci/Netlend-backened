from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_mail import Mail
from functools import wraps
from datetime import datetime, timedelta
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Configure CORS
    CORS(
        app,
        origins=[
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'http://localhost:3000',
            'http://localhost:3001'
        ],
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization']
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
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email:
            return jsonify({"success": False, "error": "Email required"}), 400
        
        from models import User
        user = User.query.filter_by(email=email).first()
        
        if user and password and user.check_password(password):
            token = create_access_token(identity=str(user.id))
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "userType": user.role.value,
                    "verified": user.verified
                },
                "token": token
            })
        
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        
        # Handle both frontend formats: 'name' or 'institution_name'
        name = data.get('name') or data.get('institution_name')
        contact_person = data.get('contact_person') or name
        email = data.get('email')
        
        if not name or not email:
            return jsonify({"success": False, "error": "Name and email are required"}), 400
        
        from models import User, UserRole
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "error": "User already exists"}), 409
        
        # Determine user role
        user_type = data.get('userType', 'lender')
        if user_type == 'admin':
            role = UserRole.ADMIN
        elif user_type == 'homebuyer':
            role = UserRole.HOMEBUYER
        else:
            role = UserRole.LENDER
            
        new_user = User(
            name=name,
            email=email,
            role=role,
            verified=role == UserRole.ADMIN
        )
        new_user.set_password(data.get('password', 'defaultpass'))
        
        db.session.add(new_user)
        db.session.commit()
        
        token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "success": True,
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "userType": new_user.role.value,
                "verified": new_user.verified
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

if __name__ == '__main__':
    app = create_app()
    print("🚀 NetLend Backend Starting...")
    print("📍 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("💚 Health: http://localhost:5000/health")
    app.run(debug=True, port=5001, host='0.0.0.0')