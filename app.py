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
    from routes.auth import auth_bp
    from routes.mortgages import mortgages_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(mortgages_bp, url_prefix='/api/mortgages')
    app.register_blueprint(mortgages_bp, url_prefix='/api', name='lender_routes')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Role-based middleware
    def token_required(allowed_roles=None):
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                user_id = get_jwt_identity()
                from models import Lender
                user = Lender.query.get_or_404(user_id)
                
                # Determine user role
                user_role = 'admin' if 'admin' in user.email.lower() else 'lender'
                
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
        
        from models import Lender
        user = Lender.query.filter_by(email=email).first()
        
        # Handle admin login
        if user and 'admin' in email.lower():
            if password and user.check_password(password):
                token = create_access_token(identity=user.id)
                return jsonify({
                    "success": True,
                    "user": {
                        "id": user.id,
                        "name": user.institution_name,
                        "email": user.email,
                        "userType": "admin",
                        "verified": user.verified
                    },
                    "token": token
                })
        # Handle regular user login (existing lender login logic)
        elif user:
            token = create_access_token(identity=user.id)
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.institution_name,
                    "email": user.email,
                    "userType": "lender",
                    "verified": user.verified
                },
                "token": token
            })
        
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        
        required_fields = ['institution_name', 'contact_person', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        from models import Lender
        if Lender.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "User already exists"}), 409
        
        new_user = Lender(
            institution_name=data['institution_name'],
            contact_person=data['contact_person'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            business_registration_number=data.get('business_registration_number'),
            verified='admin' in data['email'].lower()
        )
        new_user.set_password(data.get('password', 'defaultpass'))
        
        db.session.add(new_user)
        db.session.commit()
        
        token = create_access_token(identity=new_user.id)
        return jsonify({
            "success": True,
            "user": {
                "id": new_user.id,
                "name": new_user.institution_name,
                "email": new_user.email,
                "userType": "admin" if 'admin' in new_user.email.lower() else "lender",
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
    app.run(debug=True, port=5000, host='0.0.0.0')