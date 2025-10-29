from app import create_app, db

def update_buyer_table():
    app = create_app()
    with app.app_context():
        # Add all new columns to buyers table
        columns = [
            "ALTER TABLE buyers ADD COLUMN national_id VARCHAR(20)",
            "ALTER TABLE buyers ADD COLUMN date_of_birth DATE",
            "ALTER TABLE buyers ADD COLUMN gender VARCHAR(10)",
            "ALTER TABLE buyers ADD COLUMN county_of_residence VARCHAR(50)",
            "ALTER TABLE buyers ADD COLUMN marital_status VARCHAR(20)",
            "ALTER TABLE buyers ADD COLUMN dependents INTEGER DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN employment_status VARCHAR(20)",
            "ALTER TABLE buyers ADD COLUMN employer_name VARCHAR(200)",
            "ALTER TABLE buyers ADD COLUMN occupation VARCHAR(100)",
            "ALTER TABLE buyers ADD COLUMN employment_duration INTEGER",
            "ALTER TABLE buyers ADD COLUMN monthly_gross_income FLOAT",
            "ALTER TABLE buyers ADD COLUMN monthly_net_income FLOAT",
            "ALTER TABLE buyers ADD COLUMN other_income FLOAT DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN has_existing_loans BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN loan_types VARCHAR(500)",
            "ALTER TABLE buyers ADD COLUMN monthly_loan_repayments FLOAT DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN monthly_expenses FLOAT",
            "ALTER TABLE buyers ADD COLUMN credit_score INTEGER",
            "ALTER TABLE buyers ADD COLUMN preferred_property_type VARCHAR(20)",
            "ALTER TABLE buyers ADD COLUMN target_county VARCHAR(50)",
            "ALTER TABLE buyers ADD COLUMN estimated_property_value FLOAT",
            "ALTER TABLE buyers ADD COLUMN desired_loan_amount FLOAT",
            "ALTER TABLE buyers ADD COLUMN desired_repayment_period INTEGER",
            "ALTER TABLE buyers ADD COLUMN down_payment_amount FLOAT",
            "ALTER TABLE buyers ADD COLUMN bank_name VARCHAR(100)",
            "ALTER TABLE buyers ADD COLUMN account_number VARCHAR(50)",
            "ALTER TABLE buyers ADD COLUMN mpesa_number VARCHAR(20)",
            "ALTER TABLE buyers ADD COLUMN national_id_uploaded BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN kra_pin_uploaded BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN bank_statement_uploaded BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN credit_report_uploaded BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN proof_of_residence_uploaded BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN profile_complete BOOLEAN DEFAULT 0",
            "ALTER TABLE buyers ADD COLUMN creditworthiness_score FLOAT"
        ]
        
        with db.engine.connect() as conn:
            for sql in columns:
                try:
                    conn.execute(db.text(sql))
                    print(f"✅ Added column: {sql.split('ADD COLUMN ')[1].split(' ')[0]}")
                except Exception as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  Column already exists: {sql.split('ADD COLUMN ')[1].split(' ')[0]}")
                    else:
                        print(f"❌ Error: {e}")
            conn.commit()
        
        print("Buyer table update completed!")

if __name__ == '__main__':
    update_buyer_table()