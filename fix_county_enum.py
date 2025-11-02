#!/usr/bin/env python3

from app import create_app, db
from sqlalchemy import text

def fix_county_enum():
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Fix MURANG'A to MURANG_A in mortgage_listings table
                conn.execute(text("UPDATE mortgage_listings SET county = 'MURANG_A' WHERE county = 'MURANG''A'"))
                print("✅ Fixed MURANG'A county enum in mortgage_listings")
                
                # Fix any other potential mismatches
                conn.execute(text("UPDATE mortgage_listings SET county = 'TRANS_NZOIA' WHERE county = 'TRANS NZOIA'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'ELGEYO_MARAKWET' WHERE county = 'ELGEYO-MARAKWET'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'TAITA_TAVETA' WHERE county = 'TAITA-TAVETA'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'THARAKA_NITHI' WHERE county = 'THARAKA-NITHI'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'TANA_RIVER' WHERE county = 'TANA RIVER'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'HOMA_BAY' WHERE county = 'HOMA BAY'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'WEST_POKOT' WHERE county = 'WEST POKOT'"))
                conn.execute(text("UPDATE mortgage_listings SET county = 'UASIN_GISHU' WHERE county = 'UASIN GISHU'"))
                
                conn.commit()
                print("✅ Fixed all county enum mismatches")
            
        except Exception as e:
            print(f"❌ Error fixing county enums: {e}")

if __name__ == '__main__':
    fix_county_enum()