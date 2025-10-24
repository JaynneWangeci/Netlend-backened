from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
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
            'http://localhost:3000'
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
    
    # Add admin login endpoint
    @app.route('/api/login', methods=['POST'])
    def admin_login():
        from flask_jwt_extended import create_access_token
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"}), 400
        
        # Check if admin user exists and verify password
        from models import Lender
        user = Lender.query.filter_by(email=email).first()
        if user and 'admin' in email.lower() and user.check_password(password):
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
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
    # Add health check and docs
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "message": "NetLend API is running"})
    
    @app.route('/docs')
    def swagger_docs():
        return '''<!DOCTYPE html>
        <html><head><title>NetLend API Documentation</title></head>
        <body><h1>NetLend API Documentation</h1>
        <h2>Admin Endpoints</h2>
        <p>GET /api/admin/users - Get all users</p>
        <p>POST /api/admin/users - Create user</p>
        <p>GET /api/admin/analytics - Get analytics</p>
        <p>GET /api/admin/metrics - Get comprehensive metrics</p>
        <h2>Lender Endpoints</h2>
        <p>POST /api/mortgages/ - Create mortgage listing</p>
        <p>GET /api/lender/{id}/mortgages - Get lender mortgages</p>
        </body></html>'''
    
    @app.route('/api/lenders', methods=['GET'])
    def get_all_lenders():
        """Get all lenders - public endpoint"""
        from models import Lender
        lenders = Lender.query.all()
        return jsonify([{
            'id': lender.id,
            'name': lender.institution_name,
            'email': lender.email,
            'verified': lender.verified,
            'createdAt': lender.created_at.strftime('%Y-%m-%d')
        } for lender in lenders])

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
