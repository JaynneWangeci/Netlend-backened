#!/usr/bin/env python3
from app import create_app, db
from models import Lender

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = Lender.query.filter_by(email='admin@netlend.com').first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = Lender(
            institution_name='NetLend Admin',
            contact_person='Admin User',
            email='admin@netlend.com',
            verified=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Email: admin@netlend.com")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin_user()