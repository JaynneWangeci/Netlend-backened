from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, MortgageApplication, MortgageListing, Lender, Buyer
from datetime import datetime

homebuyer_bp = Blueprint('homebuyer', __name__)

@homebuyer_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    
    applications = MortgageApplication.query.filter_by(borrower_id=buyer_id).all()
    
    # Get active mortgages count
    from models import ActiveMortgage
    active_mortgages = ActiveMortgage.query.filter_by(borrower_id=buyer_id).count()
    
    return jsonify({
        'totalApplications': len(applications),
        'activeApplications': len([a for a in applications if a.status.value == 'pending']),
        'approvedApplications': len([a for a in applications if a.status.value == 'approved']),
        'activeMortgages': active_mortgages,
        'savedProperties': 0,
        'preApprovalStatus': 'pending'
    })

@homebuyer_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    applications = MortgageApplication.query.filter_by(borrower_id=buyer_id).all()
    
    return jsonify([{
        'id': app.id,
        'lender': app.lender.institution_name,
        'amount': app.requested_amount,
        'status': app.status.value,
        'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
        'property': f'Property {app.listing_id}'
    } for app in applications])

@homebuyer_bp.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    user_id = get_jwt_identity()
    data = request.json
    
    application = MortgageApplication(
        borrower_id=int(user_id),
        lender_id=data['lenderId'],
        listing_id=data['listingId'],
        requested_amount=data['loanAmount'],
        repayment_years=data['repaymentYears']
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'id': application.id, 'status': 'submitted'}), 201

@homebuyer_bp.route('/properties', methods=['GET'])
def get_properties():
    listings = MortgageListing.query.all()
    
    return jsonify([{
        'id': listing.id,
        'title': listing.property_title,
        'type': listing.property_type.value,
        'location': f"{listing.address}, {listing.county.value}",
        'price': float(listing.price_range),
        'rate': listing.interest_rate,
        'term': listing.repayment_period,
        'lender': listing.lender.institution_name,
        'status': listing.status.value,
        'images': listing.images or []
    } for listing in listings])

@homebuyer_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    return jsonify({
        'id': buyer.id,
        'name': buyer.name,
        'email': buyer.email,
        'phone_number': buyer.phone_number,
        'verified': buyer.verified,
        'profileComplete': buyer.profile_complete,
        'creditworthinessScore': buyer.creditworthiness_score,
        
        # Personal Information
        'nationalId': buyer.national_id,
        'dateOfBirth': buyer.date_of_birth.isoformat() if buyer.date_of_birth else None,
        'gender': buyer.gender,
        'countyOfResidence': buyer.county_of_residence.value if buyer.county_of_residence else None,
        'maritalStatus': buyer.marital_status,
        'dependents': buyer.dependents,
        
        # Employment & Income
        'employmentStatus': buyer.employment_status,
        'employerName': buyer.employer_name,
        'occupation': buyer.occupation,
        'employmentDuration': buyer.employment_duration,
        'monthlyGrossIncome': buyer.monthly_gross_income,
        'monthlyNetIncome': buyer.monthly_net_income,
        'otherIncome': buyer.other_income,
        
        # Financial Obligations
        'hasExistingLoans': buyer.has_existing_loans,
        'loanTypes': buyer.loan_types,
        'monthlyLoanRepayments': buyer.monthly_loan_repayments,
        'monthlyExpenses': buyer.monthly_expenses,
        'creditScore': buyer.credit_score,
        
        # Property Preferences
        'preferredPropertyType': buyer.preferred_property_type.value if buyer.preferred_property_type else None,
        'targetCounty': buyer.target_county.value if buyer.target_county else None,
        'estimatedPropertyValue': buyer.estimated_property_value,
        'desiredLoanAmount': buyer.desired_loan_amount,
        'desiredRepaymentPeriod': buyer.desired_repayment_period,
        'downPaymentAmount': buyer.down_payment_amount,
        
        # Banking Information
        'bankName': buyer.bank_name,
        'accountNumber': buyer.account_number,
        'mpesaNumber': buyer.mpesa_number,
        
        # Document Status
        'documentsUploaded': {
            'nationalId': buyer.national_id_uploaded,
            'kraPin': buyer.kra_pin_uploaded,
            'bankStatement': buyer.bank_statement_uploaded,
            'creditReport': buyer.credit_report_uploaded,
            'proofOfResidence': buyer.proof_of_residence_uploaded
        }
    })

@homebuyer_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    data = request.json
    
    # Personal Information
    if 'name' in data:
        buyer.name = data['name']
    if 'phoneNumber' in data:
        buyer.phone_number = data['phoneNumber']
    if 'nationalId' in data:
        buyer.national_id = data['nationalId']
    if 'dateOfBirth' in data:
        from datetime import datetime
        buyer.date_of_birth = datetime.fromisoformat(data['dateOfBirth']).date()
    if 'gender' in data:
        buyer.gender = data['gender']
    if 'countyOfResidence' in data:
        buyer.county_of_residence = KenyanCounty(data['countyOfResidence'])
    if 'maritalStatus' in data:
        buyer.marital_status = data['maritalStatus']
    if 'dependents' in data:
        buyer.dependents = data['dependents']
    
    # Employment & Income
    if 'employmentStatus' in data:
        buyer.employment_status = data['employmentStatus']
    if 'employerName' in data:
        buyer.employer_name = data['employerName']
    if 'occupation' in data:
        buyer.occupation = data['occupation']
    if 'employmentDuration' in data:
        buyer.employment_duration = data['employmentDuration']
    if 'monthlyGrossIncome' in data:
        buyer.monthly_gross_income = data['monthlyGrossIncome']
    if 'monthlyNetIncome' in data:
        buyer.monthly_net_income = data['monthlyNetIncome']
    if 'otherIncome' in data:
        buyer.other_income = data['otherIncome']
    
    # Financial Obligations
    if 'hasExistingLoans' in data:
        buyer.has_existing_loans = data['hasExistingLoans']
    if 'loanTypes' in data:
        buyer.loan_types = data['loanTypes']
    if 'monthlyLoanRepayments' in data:
        buyer.monthly_loan_repayments = data['monthlyLoanRepayments']
    if 'monthlyExpenses' in data:
        buyer.monthly_expenses = data['monthlyExpenses']
    if 'creditScore' in data:
        buyer.credit_score = data['creditScore']
    
    # Property Preferences
    if 'preferredPropertyType' in data:
        buyer.preferred_property_type = PropertyType(data['preferredPropertyType'])
    if 'targetCounty' in data:
        buyer.target_county = KenyanCounty(data['targetCounty'])
    if 'estimatedPropertyValue' in data:
        buyer.estimated_property_value = data['estimatedPropertyValue']
    if 'desiredLoanAmount' in data:
        buyer.desired_loan_amount = data['desiredLoanAmount']
    if 'desiredRepaymentPeriod' in data:
        buyer.desired_repayment_period = data['desiredRepaymentPeriod']
    if 'downPaymentAmount' in data:
        buyer.down_payment_amount = data['downPaymentAmount']
    
    # Banking Information
    if 'bankName' in data:
        buyer.bank_name = data['bankName']
    if 'accountNumber' in data:
        buyer.account_number = data['accountNumber']
    if 'mpesaNumber' in data:
        buyer.mpesa_number = data['mpesaNumber']
    
    # Calculate creditworthiness score
    buyer.calculate_creditworthiness_score()
    
    # Check if profile is complete
    required_fields = [
        buyer.national_id, buyer.monthly_net_income, buyer.employment_status,
        buyer.estimated_property_value, buyer.desired_loan_amount, buyer.bank_name
    ]
    buyer.profile_complete = all(field is not None for field in required_fields)
    
    db.session.commit()
    return jsonify({
        'success': True,
        'profileComplete': buyer.profile_complete,
        'creditworthinessScore': buyer.creditworthiness_score
    })

@homebuyer_bp.route('/prequalify', methods=['POST'])
@jwt_required()
def prequalify():
    data = request.json
    
    # Simple eligibility calculation
    income = data.get('income', 0)
    loan_amount = data.get('loanAmount', 0)
    
    eligibility_score = min(90, (income * 12 * 5) / loan_amount * 100) if loan_amount > 0 else 0
    
    return jsonify({
        'eligibilityScore': round(eligibility_score),
        'maxLoanAmount': income * 12 * 5,
        'status': 'qualified' if eligibility_score > 70 else 'review_required'
    })

@homebuyer_bp.route('/lenders', methods=['GET'])
def get_lenders():
    lenders = Lender.query.filter_by(verified=True).all()
    
    return jsonify([{
        'id': lender.id,
        'name': lender.institution_name,
        'email': lender.email,
        'verified': lender.verified
    } for lender in lenders])

@homebuyer_bp.route('/pre-approval', methods=['GET'])
@jwt_required()
def get_pre_approval():
    return jsonify({
        'status': 'pending',
        'amount': 0,
        'expiryDate': None
    })

@homebuyer_bp.route('/saved-properties', methods=['GET'])
@jwt_required()
def get_saved_properties():
    return jsonify([])

@homebuyer_bp.route('/documents', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    data = request.json
    
    document_type = data.get('documentType')
    
    # Update document upload status
    if document_type == 'nationalId':
        buyer.national_id_uploaded = True
    elif document_type == 'kraPin':
        buyer.kra_pin_uploaded = True
    elif document_type == 'bankStatement':
        buyer.bank_statement_uploaded = True
    elif document_type == 'creditReport':
        buyer.credit_report_uploaded = True
    elif document_type == 'proofOfResidence':
        buyer.proof_of_residence_uploaded = True
    
    # Recalculate creditworthiness score
    buyer.calculate_creditworthiness_score()
    
    db.session.commit()
    return jsonify({
        'success': True,
        'creditworthinessScore': buyer.creditworthiness_score
    })

@homebuyer_bp.route('/creditworthiness', methods=['GET'])
@jwt_required()
def get_creditworthiness():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    # Recalculate score
    score = buyer.calculate_creditworthiness_score()
    db.session.commit()
    
    # Determine risk level
    if score >= 80:
        risk_level = 'Low Risk'
        recommendation = 'Excellent candidate for mortgage approval'
    elif score >= 60:
        risk_level = 'Medium Risk'
        recommendation = 'Good candidate with minor considerations'
    elif score >= 40:
        risk_level = 'High Risk'
        recommendation = 'Requires additional documentation or guarantor'
    else:
        risk_level = 'Very High Risk'
        recommendation = 'May need to improve financial standing'
    
    return jsonify({
        'score': score,
        'riskLevel': risk_level,
        'recommendation': recommendation,
        'profileComplete': buyer.profile_complete
    })

@homebuyer_bp.route('/my-mortgages', methods=['GET'])
@jwt_required()
def get_my_mortgages():
    user_id = get_jwt_identity()
    buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
    
    # Get active mortgages for this buyer
    from models import ActiveMortgage
    mortgages = ActiveMortgage.query.filter_by(borrower_id=buyer_id).all()
    
    result = []
    for mortgage in mortgages:
        # Calculate remaining payments
        monthly_payment = (mortgage.principal_amount * (mortgage.interest_rate/100/12)) / (1 - (1 + mortgage.interest_rate/100/12)**(-mortgage.repayment_term))
        payments_made = mortgage.repayment_term - int((mortgage.remaining_balance / mortgage.principal_amount) * mortgage.repayment_term)
        
        result.append({
            'id': mortgage.id,
            'lender': mortgage.lender.institution_name,
            'property': mortgage.application.listing.property_title if mortgage.application and mortgage.application.listing else 'Property',
            'principalAmount': mortgage.principal_amount,
            'remainingBalance': mortgage.remaining_balance,
            'interestRate': mortgage.interest_rate,
            'monthlyPayment': round(monthly_payment, 2),
            'totalTerm': mortgage.repayment_term,
            'paymentsMade': payments_made,
            'remainingPayments': mortgage.repayment_term - payments_made,
            'nextPaymentDue': mortgage.next_payment_due.isoformat() if mortgage.next_payment_due else None,
            'status': mortgage.status.value,
            'startDate': mortgage.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(result)

