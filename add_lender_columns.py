#!/usr/bin/env python3
"""
Simple script to add new columns to lenders table
"""

import sqlite3
import os

def add_lender_columns():
    """Add new columns to lenders table using raw SQL"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'netlend.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of new columns to add
    new_columns = [
        ('company_type', 'VARCHAR(50)'),
        ('website', 'VARCHAR(255)'),
        ('established_year', 'INTEGER'),
        ('license_number', 'VARCHAR(100)'),
        ('street_address', 'VARCHAR(255)'),
        ('city', 'VARCHAR(100)'),
        ('county', 'VARCHAR(50)'),
        ('postal_code', 'VARCHAR(20)'),
        ('secondary_phone', 'VARCHAR(20)'),
        ('fax_number', 'VARCHAR(20)'),
        ('customer_service_email', 'VARCHAR(120)'),
        ('description', 'TEXT'),
        ('services_offered', 'JSON'),
        ('operating_hours', 'JSON')
    ]
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(lenders)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns if they don't exist
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE lenders ADD COLUMN {column_name} {column_type}")
                    print(f"✓ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ Failed to add {column_name}: {e}")
            else:
                print(f"- Column {column_name} already exists")
        
        conn.commit()
        print("✓ Database migration completed successfully")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_lender_columns()