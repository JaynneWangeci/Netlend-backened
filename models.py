# NetLend Backend - Database Models
# This file defines all database tables, relationships, and business logic
# Uses SQLAlchemy ORM for database operations and Python Enums for controlled vocabularies

from app import db  # Database instance from main app
from datetime import datetime  # For timestamp fields
from werkzeug.security import generate_password_hash, check_password_hash  # Secure password handling
from enum import Enum  # For creating controlled vocabulary enums

# ENUMERATION CLASSES
# These define controlled vocabularies for various fields to ensure data consistency
# and prevent invalid values from being stored in the database

class UserRole(Enum):
    """Defines the three main user types in the system"""
    ADMIN = "admin"        # Platform administrators
    LENDER = "lender"      # Financial institutions offering mortgages
    HOMEBUYER = "homebuyer" # Individuals seeking mortgage financing

class PropertyType(Enum):
    """Types of properties available for mortgage financing"""
    APARTMENT = "apartment"   # Multi-unit residential buildings
    BUNGALOW = "bungalow"     # Single-story detached houses
    TOWNHOUSE = "townhouse"   # Multi-story attached houses
    VILLA = "villa"           # Luxury detached houses

class ListingStatus(Enum):
    """Property listing status - tracks the lifecycle of mortgage opportunities"""
    ACTIVE = "active"       # Available for mortgage applications
    ACQUIRED = "acquired"   # Property purchased but mortgage not fully paid
    SOLD = "sold"           # Property fully paid off and mortgage completed

class ApplicationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_INFO = "needs_info"

class MortgageStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"
    REFINANCED = "refinanced"

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    LATE = "late"
    MISSED = "missed"

class OfferStatus(Enum):
    OFFERED = "offered"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class KenyanCounty(Enum):
    BARINGO = "Baringo"
    BOMET = "Bomet"
    BUNGOMA = "Bungoma"
    BUSIA = "Busia"
    ELGEYO_MARAKWET = "Elgeyo-Marakwet"
    EMBU = "Embu"
    GARISSA = "Garissa"
    HOMA_BAY = "Homa Bay"
    ISIOLO = "Isiolo"
    KAJIADO = "Kajiado"
    KAKAMEGA = "Kakamega"
    KERICHO = "Kericho"
    KIAMBU = "Kiambu"
    KILIFI = "Kilifi"
    KIRINYAGA = "Kirinyaga"
    KISII = "Kisii"
    KISUMU = "Kisumu"
    KITUI = "Kitui"
    KWALE = "Kwale"
    LAIKIPIA = "Laikipia"
    LAMU = "Lamu"
    MACHAKOS = "Machakos"
    MAKUENI = "Makueni"
    MANDERA = "Mandera"
    MARSABIT = "Marsabit"
    MERU = "Meru"
    MIGORI = "Migori"
    MOMBASA = "Mombasa"
    MURANG_A = "Murang'a"
    NAIROBI = "Nairobi"
    NAKURU = "Nakuru"
    NANDI = "Nandi"
    NAROK = "Narok"
    NYAMIRA = "Nyamira"
    NYANDARUA = "Nyandarua"
    NYERI = "Nyeri"
    SAMBURU = "Samburu"
    SIAYA = "Siaya"
    TAITA_TAVETA = "Taita-Taveta"
    TANA_RIVER = "Tana River"
    THARAKA_NITHI = "Tharaka-Nithi"
    TRANS_NZOIA = "Trans Nzoia"
    TURKANA = "Turkana"
    UASIN_GISHU = "Uasin Gishu"
    VIHIGA = "Vihiga"
    WAJIR = "Wajir"
    WEST_POKOT = "West Pokot"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Buyer(db.Model):
    """Homebuyer model - stores comprehensive profile information for mortgage assessment
    
    This model contains 34+ fields covering all aspects needed for mortgage evaluation:
    - Personal information (name, contact, demographics)
    - Employment and income details
    - Financial obligations and credit history
    - Property preferences and loan requirements
    - Banking information and document verification status
    """
    __tablename__ = 'buyers'
    
    # BASIC ACCOUNT INFORMATION
    id = db.Column(db.Integer, primary_key=True)  # Unique buyer identifier
    name = db.Column(db.String(200), nullable=False)  # Full legal name
    email = db.Column(db.String(120), unique=True, nullable=False)  # Login email (unique)
    password_hash = db.Column(db.String(255), nullable=False)  # Encrypted password
    phone_number = db.Column(db.String(20))  # Primary contact number
    verified = db.Column(db.Boolean, default=False)  # Account verification status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Registration timestamp
    
    # Personal Information
    national_id = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    county_of_residence = db.Column(db.Enum(KenyanCounty))
    marital_status = db.Column(db.String(20))
    dependents = db.Column(db.Integer, default=0)
    
    # Employment & Income
    employment_status = db.Column(db.String(20))
    employer_name = db.Column(db.String(200))
    occupation = db.Column(db.String(100))
    employment_duration = db.Column(db.Integer)  # months
    monthly_gross_income = db.Column(db.Float)
    monthly_net_income = db.Column(db.Float)
    other_income = db.Column(db.Float, default=0)
    
    # Financial Obligations
    has_existing_loans = db.Column(db.Boolean, default=False)
    loan_types = db.Column(db.String(500))
    monthly_loan_repayments = db.Column(db.Float, default=0)
    monthly_expenses = db.Column(db.Float)
    credit_score = db.Column(db.Integer)
    
    # Property Preferences
    preferred_property_type = db.Column(db.Enum(PropertyType))
    target_county = db.Column(db.Enum(KenyanCounty))
    estimated_property_value = db.Column(db.Float)
    desired_loan_amount = db.Column(db.Float)
    desired_repayment_period = db.Column(db.Integer)  # years
    down_payment_amount = db.Column(db.Float)
    
    # Banking Information
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    mpesa_number = db.Column(db.String(20))
    
    # Document Verification
    national_id_uploaded = db.Column(db.Boolean, default=False)
    kra_pin_uploaded = db.Column(db.Boolean, default=False)
    bank_statement_uploaded = db.Column(db.Boolean, default=False)
    credit_report_uploaded = db.Column(db.Boolean, default=False)
    proof_of_residence_uploaded = db.Column(db.Boolean, default=False)
    
    # Profile Completion
    profile_complete = db.Column(db.Boolean, default=False)
    creditworthiness_score = db.Column(db.Float)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def calculate_creditworthiness_score(self):
        """Calculate creditworthiness score based on profile data
        
        This algorithm evaluates mortgage eligibility using a weighted scoring system:
        - Income to loan ratio (40% weight): Measures ability to afford payments
        - Employment stability (20% weight): Job security assessment
        - Down payment percentage (20% weight): Financial commitment level
        - Existing loan burden (10% weight): Current debt obligations
        - Document completeness (10% weight): Application readiness
        
        Returns a score from 0-100, where higher scores indicate better creditworthiness
        """
        score = 0
        
        # INCOME TO LOAN RATIO ASSESSMENT (40% of total score)
        # This is the most important factor - can the buyer afford the monthly payments?
        if self.monthly_net_income and self.desired_loan_amount:
            # Estimate monthly payment using 12% annual interest rate
            monthly_payment = (self.desired_loan_amount * 0.12) / 12
            income_ratio = monthly_payment / self.monthly_net_income
            
            # Score based on payment-to-income ratio (lower is better)
            if income_ratio < 0.3:      # Less than 30% of income - excellent
                score += 40
            elif income_ratio < 0.4:    # 30-40% of income - good
                score += 30
            elif income_ratio < 0.5:    # 40-50% of income - acceptable
                score += 20
            # Above 50% gets 0 points - too risky
        
        # Employment stability (20% weight)
        if self.employment_duration:
            if self.employment_duration >= 24:
                score += 20
            elif self.employment_duration >= 12:
                score += 15
            elif self.employment_duration >= 6:
                score += 10
        
        # Down payment percentage (20% weight)
        if self.down_payment_amount and self.estimated_property_value:
            down_payment_ratio = self.down_payment_amount / self.estimated_property_value
            if down_payment_ratio >= 0.3:
                score += 20
            elif down_payment_ratio >= 0.2:
                score += 15
            elif down_payment_ratio >= 0.1:
                score += 10
        
        # Existing loan burden (10% weight)
        if self.monthly_net_income and self.monthly_loan_repayments:
            loan_burden = self.monthly_loan_repayments / self.monthly_net_income
            if loan_burden < 0.2:
                score += 10
            elif loan_burden < 0.3:
                score += 7
            elif loan_burden < 0.4:
                score += 5
        
        # Document completeness (10% weight)
        docs_uploaded = sum([
            self.national_id_uploaded,
            self.kra_pin_uploaded,
            self.bank_statement_uploaded,
            self.proof_of_residence_uploaded
        ])
        score += (docs_uploaded / 4) * 10
        
        self.creditworthiness_score = min(100, score)
        return self.creditworthiness_score

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Lender(db.Model):
    __tablename__ = 'lenders'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    business_registration_number = db.Column(db.String(50))
    verified = db.Column(db.Boolean, default=False)
    logo_url = db.Column(db.String(255))
    
    # Company Details
    company_type = db.Column(db.String(50))  # Bank, SACCO, Microfinance, etc.
    website = db.Column(db.String(255))
    established_year = db.Column(db.Integer)
    license_number = db.Column(db.String(100))
    
    # Address Information
    street_address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    county = db.Column(db.Enum(KenyanCounty))
    postal_code = db.Column(db.String(20))
    
    # Additional Contact Information
    secondary_phone = db.Column(db.String(20))
    fax_number = db.Column(db.String(20))
    customer_service_email = db.Column(db.String(120))
    
    # Business Information
    description = db.Column(db.Text)
    services_offered = db.Column(db.JSON)  # Array of services
    operating_hours = db.Column(db.JSON)  # Business hours
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mortgage_listings = db.relationship('MortgageListing', backref='lender', lazy=True)
    applications = db.relationship('MortgageApplication', backref='lender', lazy=True)
    active_mortgages = db.relationship('ActiveMortgage', backref='lender', lazy=True)
    refinancing_offers = db.relationship('RefinancingOffer', backref='lender', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MortgageListing(db.Model):
    __tablename__ = 'mortgage_listings'
    
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    property_title = db.Column(db.String(200), nullable=False)
    property_type = db.Column(db.Enum(PropertyType), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False, default=3)
    address = db.Column(db.String(255), nullable=False)
    county = db.Column(db.Enum(KenyanCounty), nullable=False)
    price_range = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    repayment_period = db.Column(db.Integer, nullable=False)  # years
    down_payment = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float)
    eligibility_criteria = db.Column(db.Text)
    images = db.Column(db.JSON)
    status = db.Column(db.Enum(ListingStatus), default=ListingStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('MortgageApplication', backref='listing', lazy=True)
    
    def update_status_from_payments(self):
        """Update house status based on mortgage payments"""
        active_mortgage = ActiveMortgage.query.join(MortgageApplication).filter(
            MortgageApplication.listing_id == self.id,
            ActiveMortgage.status == MortgageStatus.ACTIVE
        ).first()
        
        if not active_mortgage:
            return
        
        total_paid = active_mortgage.principal_amount - active_mortgage.remaining_balance
        payment_percentage = total_paid / active_mortgage.principal_amount
        
        if payment_percentage >= 1.0:
            self.status = ListingStatus.SOLD
        elif payment_percentage > 0:
            self.status = ListingStatus.ACQUIRED
        
        db.session.commit()

class MortgageApplication(db.Model):
    __tablename__ = 'mortgage_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, nullable=False)  # Reference to borrower (handled by other team)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('mortgage_listings.id'), nullable=False)
    requested_amount = db.Column(db.Float, nullable=False)
    repayment_years = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    active_mortgage = db.relationship('ActiveMortgage', backref='application', uselist=False)

class ActiveMortgage(db.Model):
    __tablename__ = 'active_mortgages'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('mortgage_applications.id'), nullable=False)
    borrower_id = db.Column(db.Integer, nullable=False)  # Reference to borrower
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    repayment_term = db.Column(db.Integer, nullable=False)  # months
    next_payment_due = db.Column(db.Date)
    remaining_balance = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(MortgageStatus), default=MortgageStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payment_schedules = db.relationship('PaymentSchedule', backref='mortgage', lazy=True)
    refinancing_offers = db.relationship('RefinancingOffer', backref='mortgage', lazy=True)

class PaymentSchedule(db.Model):
    __tablename__ = 'payment_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    mortgage_id = db.Column(db.Integer, db.ForeignKey('active_mortgages.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    receipt_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def process_payment(self, amount):
        """Process payment and update house status"""
        self.amount_paid = amount
        self.status = PaymentStatus.PAID if amount >= self.amount_due else PaymentStatus.PENDING
        
        # Update remaining balance
        self.mortgage.remaining_balance -= amount
        
        # Update house status
        if self.mortgage.application and self.mortgage.application.listing:
            self.mortgage.application.listing.update_status_from_payments()
        
        db.session.commit()
    
    def calculate_monthly_payment(listing):
        """Calculate monthly payment using standard mortgage formula"""
        loan_amount = float(listing.price_range) - listing.down_payment
        monthly_rate = listing.interest_rate / 100 / 12
        num_payments = listing.repayment_period * 12
        
        if monthly_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        
        listing.monthly_payment = round(monthly_payment, 2)
        return listing.monthly_payment

class RefinancingOffer(db.Model):
    __tablename__ = 'refinancing_offers'
    
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    mortgage_id = db.Column(db.Integer, db.ForeignKey('active_mortgages.id'), nullable=False)
    new_interest_rate = db.Column(db.Float, nullable=False)
    new_term = db.Column(db.Integer, nullable=False)
    offer_expiry = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(OfferStatus), default=OfferStatus.OFFERED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LenderAnalytics(db.Model):
    __tablename__ = 'lender_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    total_loans_disbursed = db.Column(db.Integer, default=0)
    total_amount_issued = db.Column(db.Float, default=0)
    active_loans = db.Column(db.Integer, default=0)
    revenue_from_interest = db.Column(db.Float, default=0)
    default_rate = db.Column(db.Float, default=0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    lender = db.relationship('Lender', backref='analytics')

class SavedProperty(db.Model):
    __tablename__ = 'saved_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('mortgage_listings.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    buyer = db.relationship('Buyer', backref='saved_properties')
    listing = db.relationship('MortgageListing', backref='saved_by_buyers')

class PreApproval(db.Model):
    __tablename__ = 'pre_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=False)
    approved_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    valid_until = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lenders.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)