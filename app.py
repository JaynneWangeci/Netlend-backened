from flask import Flask
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
    
    # Admin routes
    from routes.admin import admin_bp

    # Lender routes (if different from mortgages)
    from routes.lenders import lenders_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(mortgages_bp, url_prefix='/api/mortgages')
    app.register_blueprint(lenders_bp, url_prefix='/api/lenders')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
