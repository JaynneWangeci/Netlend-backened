#!/usr/bin/env python3

from app import create_app, db
from sqlalchemy import text

def add_description_field():
    app = create_app()
    
    with app.app_context():
        try:
            # Add description column to mortgage_listings table
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE mortgage_listings ADD COLUMN description VARCHAR(100)"))
                conn.commit()
            print("✅ Added description column to mortgage_listings table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✅ Description column already exists")
            else:
                print(f"❌ Error adding description column: {e}")

if __name__ == '__main__':
    add_description_field()