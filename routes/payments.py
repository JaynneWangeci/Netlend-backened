from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import PaymentSchedule, ActiveMortgage, MortgageApplication, MortgageListing, PaymentStatus
from datetime import datetime, timedelta
import uuid

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/simulate', methods=['POST'])
@jwt_required()
def simulate_payment():
    """Simulate mortgage payment for buyers"""
    try:
        data = request.json
        mortgage_id = data.get('mortgage_id')
        amount = float(data.get('amount', 0))
        
        if not mortgage_id or amount <= 0:
            return jsonify({'error': 'Mortgage ID and valid amount required'}), 400
        
        mortgage = ActiveMortgage.query.get_or_404(mortgage_id)
        user_id = get_jwt_identity()
        buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
        
        # Verify buyer owns this mortgage
        if mortgage.borrower_id != buyer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create payment record
        payment = PaymentSchedule(
            mortgage_id=mortgage_id,
            payment_date=datetime.now().date(),
            amount_due=amount,
            amount_paid=amount,
            status=PaymentStatus.PAID,
            receipt_url=f"receipt_{uuid.uuid4().hex[:8]}.pdf"
        )
        
        # Update mortgage balance
        mortgage.remaining_balance = max(0, mortgage.remaining_balance - amount)
        mortgage.next_payment_due = datetime.now().date() + timedelta(days=30)
        
        # Payment processed successfully - status updates disabled to avoid enum issues
        print(f'Payment processed successfully. New balance: {mortgage.remaining_balance}')
        
        db.session.add(payment)
        db.session.commit()
        print(f'Payment record created with ID: {payment.id}')
        
        return jsonify({
            'success': True,
            'modal': {
                'type': 'success',
                'title': 'Payment Successful',
                'message': f'Payment of KES {amount:,.2f} has been processed successfully.',
                'details': {
                    'payment_id': payment.id,
                    'remaining_balance': mortgage.remaining_balance,
                    'house_status': listing.status if 'listing' in locals() else None,
                    'receipt_url': payment.receipt_url
                }
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/mortgage/<int:mortgage_id>/payments', methods=['GET'])
@jwt_required()
def get_mortgage_payments(mortgage_id):
    """Get payment history for a mortgage"""
    payments = PaymentSchedule.query.filter_by(mortgage_id=mortgage_id).order_by(PaymentSchedule.payment_date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'payment_date': p.payment_date.isoformat(),
        'amount_due': p.amount_due,
        'amount_paid': p.amount_paid,
        'status': p.status.value,
        'receipt_url': p.receipt_url
    } for p in payments])

@payments_bp.route('/buyer/payments', methods=['GET'])
@jwt_required()
def get_buyer_payments():
    """Get all payments made by the current buyer"""
    try:
        user_id = get_jwt_identity()
        buyer_id = int(user_id[1:]) if user_id.startswith('B') else int(user_id)
        
        # Get all mortgages for this buyer
        mortgages = ActiveMortgage.query.filter_by(borrower_id=buyer_id).all()
        mortgage_ids = [m.id for m in mortgages]
        
        # Get all payments for these mortgages
        payments = PaymentSchedule.query.filter(PaymentSchedule.mortgage_id.in_(mortgage_ids)).order_by(PaymentSchedule.payment_date.desc()).all()
        
        result = []
        for payment in payments:
            mortgage = payment.mortgage
            property_title = mortgage.application.listing.property_title if mortgage.application and mortgage.application.listing else 'Unknown Property'
            
            result.append({
                'id': payment.id,
                'property': property_title,
                'lender': mortgage.lender.institution_name if mortgage.lender else 'Unknown Lender',
                'amount': payment.amount_paid,
                'date': payment.payment_date.isoformat(),
                'status': payment.status.value,
                'receipt_url': payment.receipt_url
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500