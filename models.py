from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    LENDER = "lender"
    HOMEBUYER = "homebuyer"

class PropertyType(Enum):
    APARTMENT = "apartment"
    BUNGALOW = "bungalow"
    TOWNHOUSE = "townhouse"
    VILLA = "villa"

class ListingStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    REMOVED = "removed"

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
    __tablename__ = 'buyers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    address = db.Column(db.String(255), nullable=False)
    county = db.Column(db.Enum(KenyanCounty), nullable=False)
    price_range = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    repayment_period = db.Column(db.Integer, nullable=False)  # years
    down_payment = db.Column(db.Float, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    images = db.Column(db.JSON)
    status = db.Column(db.Enum(ListingStatus), default=ListingStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('MortgageApplication', backref='listing', lazy=True)

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