from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, MortgageApplication, MortgageListing, Lender, Buyer, KenyanCounty, PropertyType
from datetime import datetime

homebuyer_bp = Blueprint('homebuyer', __name__)

@homebuyer_bp.route('/test-applications', methods=['POST'])
def test_applications():
    return jsonify({'message': 'Applications endpoint working', 'data': request.json})

@homebuyer_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    if isinstance(user_id, str) and len(user_id) > 1 and user_id[0] in ['L', 'B', 'A', 'U']:
        buyer_id = int(user_id[1:])
    else:
        buyer_id = int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404
    
    return jsonify({
        'name': buyer.name or '',
        'fullName': buyer.name or '',
        'buyerName': buyer.name or '',
        'email': buyer.email or '',
        'phoneNumber': buyer.phone_number or '',
        'nationalId': buyer.national_id or '',
        'gender': buyer.gender or '',
        'maritalStatus': buyer.marital_status or '',
        'dependents': buyer.dependents or 0,
        'employmentStatus': buyer.employment_status or '',
        'employerName': buyer.employer_name or '',
        'monthlyGrossIncome': buyer.monthly_gross_income or '',
        'monthlyNetIncome': buyer.monthly_net_income or '',
        'monthlyExpenses': buyer.monthly_expenses or '',
        'hasExistingLoans': buyer.has_existing_loans or False,
        'monthlyLoanRepayments': buyer.monthly_loan_repayments or '',
        'estimatedPropertyValue': buyer.estimated_property_value or '',
        'desiredLoanAmount': buyer.desired_loan_amount or '',
        'downPaymentAmount': buyer.down_payment_amount or '',
        'bankName': buyer.bank_name or '',
        'accountNumber': buyer.account_number or '',
        'mpesaNumber': buyer.mpesa_number or '',
        'profileComplete': buyer.profile_complete or False,
        'creditworthinessScore': buyer.creditworthiness_score or 0
    })

@homebuyer_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        if isinstance(user_id, str) and len(user_id) > 1 and user_id[0] in ['L', 'B', 'A', 'U']:
            buyer_id = int(user_id[1:])
        else:
            buyer_id = int(user_id)
        buyer = Buyer.query.get(buyer_id)
        
        if not buyer:
            return jsonify({'error': 'Buyer not found'}), 404
            
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f'Profile update data received: {data}')  # Debug log
        
        # Personal Information
        if 'name' in data:
            buyer.name = data['name']
        if 'phoneNumber' in data:
            buyer.phone_number = data['phoneNumber']
        if 'nationalId' in data:
            buyer.national_id = data['nationalId']
        if 'gender' in data:
            buyer.gender = data['gender']
        if 'maritalStatus' in data:
            buyer.marital_status = data['maritalStatus']
        if 'dependents' in data:
            buyer.dependents = int(data['dependents']) if data['dependents'] else 0
        
        # Employment & Income
        if 'employmentStatus' in data:
            buyer.employment_status = data['employmentStatus']
        if 'employerName' in data:
            buyer.employer_name = data['employerName'] if data['employerName'] else None
        if 'monthlyGrossIncome' in data:
            buyer.monthly_gross_income = float(data['monthlyGrossIncome']) if data['monthlyGrossIncome'] else None
        if 'monthlyNetIncome' in data:
            buyer.monthly_net_income = float(data['monthlyNetIncome']) if data['monthlyNetIncome'] else None
        
        # Banking Information
        if 'bankName' in data:
            buyer.bank_name = data['bankName']
        if 'accountNumber' in data:
            buyer.account_number = data['accountNumber']
        if 'mpesaNumber' in data:
            buyer.mpesa_number = data['mpesaNumber']
        if 'mpesa_number' in data:
            buyer.mpesa_number = data['mpesa_number']
        if 'mpesa' in data:
            buyer.mpesa_number = data['mpesa']
        
        # Calculate creditworthiness score
        if buyer.calculate_creditworthiness_score:
            buyer.calculate_creditworthiness_score()
        
        db.session.add(buyer)
        db.session.commit()
        return jsonify({
            'success': True,
            'profileComplete': buyer.profile_complete,
            'creditworthinessScore': buyer.creditworthiness_score
        })
    except Exception as e:
        print(f'Profile update error: {e}')
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@homebuyer_bp.route('/properties', methods=['GET'])
def get_properties():
    # Get filter parameters
    min_payment = request.args.get('minPayment', type=float)
    max_payment = request.args.get('maxPayment', type=float)
    
    # Build query with filters
    query = MortgageListing.query
    
    if min_payment:
        query = query.filter(MortgageListing.monthly_payment >= min_payment)
    if max_payment:
        query = query.filter(MortgageListing.monthly_payment <= max_payment)
    
    listings = query.all()
    
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
        'monthlyPayment': listing.monthly_payment,
        'images': listing.images or []
    } for listing in listings])

@homebuyer_bp.route('/creditworthiness', methods=['GET'])
@jwt_required()
def get_creditworthiness():
    user_id = get_jwt_identity()
    if isinstance(user_id, str) and len(user_id) > 1 and user_id[0] in ['L', 'B', 'A', 'U']:
        buyer_id = int(user_id[1:])
    else:
        buyer_id = int(user_id)
    buyer = Buyer.query.get(buyer_id)
    
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404
    
    score = buyer.calculate_creditworthiness_score()
    db.session.commit()
    
    # Determine eligibility level
    if score >= 80:
        level = 'Highly Eligible'
        color = 'green'
        recommendation = 'Excellent candidate for mortgage approval'
    elif score >= 60:
        level = 'Eligible'
        color = 'blue'
        recommendation = 'Good candidate with strong profile'
    elif score >= 40:
        level = 'Conditionally Eligible'
        color = 'orange'
        recommendation = 'May require additional documentation'
    else:
        level = 'Not Eligible'
        color = 'red'
        recommendation = 'Profile needs improvement before approval'
    
    return jsonify({
        'score': score,
        'maxScore': 110,
        'eligibilityLevel': level,
        'color': color,
        'recommendation': recommendation,
        'profileComplete': buyer.profile_complete
    })

@homebuyer_bp.route('/my-mortgages', methods=['GET'])
@jwt_required()
def get_my_mortgages():
    try:
        user_id = get_jwt_identity()
        buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
        
        from models import ActiveMortgage
        mortgages = ActiveMortgage.query.filter_by(borrower_id=buyer_id).all()
        
        result = []
        for mortgage in mortgages:
            try:
                if mortgage.interest_rate > 0:
                    monthly_rate = mortgage.interest_rate / 100 / 12
                    monthly_payment = (mortgage.principal_amount * monthly_rate) / (1 - (1 + monthly_rate)**(-mortgage.repayment_term))
                else:
                    monthly_payment = mortgage.principal_amount / mortgage.repayment_term
                
                payments_made = mortgage.repayment_term - int((mortgage.remaining_balance / mortgage.principal_amount) * mortgage.repayment_term)
                
                result.append({
                    'id': mortgage.id,
                    'lender': mortgage.lender.institution_name if mortgage.lender else 'Unknown Lender',
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
            except Exception as e:
                print(f'Error processing mortgage {mortgage.id}: {e}')
                continue
        
        return jsonify(result)
    except Exception as e:
        print(f'My mortgages error: {e}')
        return jsonify({'error': str(e)}), 500

@homebuyer_bp.route('/applications', methods=['GET', 'POST'])
@jwt_required()
def handle_applications():
    if request.method == 'GET':
        try:
            user_id = get_jwt_identity()
            print(f'User trying to access applications: {user_id}')
            if user_id.startswith('B'):
                buyer_id = int(user_id[1:])
            elif user_id.startswith('L'):
                buyer_id = int(user_id[1:])  # Use lender ID as buyer ID for testing
            else:
                buyer_id = int(user_id)
            print(f'Getting applications for buyer ID: {buyer_id}')
            applications = MortgageApplication.query.filter_by(borrower_id=buyer_id).all()
            print(f'Found {len(applications)} applications for buyer {buyer_id}')
            
            return jsonify([{
                'id': app.id,
                'lender': app.lender.institution_name if app.lender else 'Unknown Lender',
                'amount': app.requested_amount,
                'status': app.status.value,
                'submittedAt': app.submitted_at.strftime('%Y-%m-%d'),
                'property': app.listing.property_title if app.listing else 'Unknown Property'
            } for app in applications])
        except Exception as e:
            print(f'Applications GET error: {e}')
            return jsonify({'error': str(e)}), 500
    
    # POST method (existing create application logic)
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        print(f'Application data: {data}')
        print(f'User ID: {user_id}')
        
        # Get property details
        listing_id = data.get('property_id') or data.get('id')
        print(f'Listing ID: {listing_id}')
        
        # Get lender_id from the listing
        listing = MortgageListing.query.get(listing_id)
        if not listing:
            print(f'Listing not found for ID: {listing_id}')
            return jsonify({'error': 'Property not found'}), 404
        
        print(f'Found listing: {listing.property_title}, Lender ID: {listing.lender_id}')
        
        loan_amount = data.get('loan_amount') or (data.get('property_price', 0) * 0.8)
        repayment_years = data.get('repayment_period') or data.get('term', 25)
        
        print(f'Loan amount: {loan_amount}, Repayment years: {repayment_years}')
        
        borrower_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
        
        # Check if buyer already applied for this property
        existing_app = MortgageApplication.query.filter_by(
            borrower_id=borrower_id,
            listing_id=listing_id
        ).first()
        
        if existing_app:
            return jsonify({'error': 'You have already applied for this property'}), 409
        
        print(f'Creating application: borrower_id={borrower_id}, lender_id={listing.lender_id}, listing_id={listing_id}')
        
        application = MortgageApplication(
            borrower_id=borrower_id,
            lender_id=listing.lender_id,
            listing_id=listing_id,
            requested_amount=loan_amount,
            repayment_years=repayment_years
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({'id': application.id, 'status': 'submitted'}), 201
    except Exception as e:
        print(f'Application error: {e}')
        db.session.rollback()
        return jsonify({'error': str(e)}), 500