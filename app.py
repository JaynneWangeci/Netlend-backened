from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:3000'], supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])
    mail.init_app(app)
    
    from routes.auth import auth_bp
    from routes.mortgages import mortgages_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(mortgages_bp, url_prefix='/api/mortgages')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)