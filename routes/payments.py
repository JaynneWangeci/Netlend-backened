from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import PaymentSchedule, ActiveMortgage, MortgageApplication, MortgageListing

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/process', methods=['POST'])
@jwt_required()
def process_payment():
    """Process mortgage payment and update house status automatically"""
    data = request.json
    payment_id = data.get('payment_id')
    amount = data.get('amount')
    
    if not payment_id or not amount:
        return jsonify({'error': 'Payment ID and amount required'}), 400
    
    payment = PaymentSchedule.query.get_or_404(payment_id)
    
    # Process the payment
    payment.process_payment(amount)
    
    # Get updated house status
    listing = payment.mortgage.application.listing if payment.mortgage.application else None
    
    return jsonify({
        'success': True,
        'message': 'Payment processed successfully',
        'house_status': listing.status.value if listing else None,
        'remaining_balance': payment.mortgage.remaining_balance
    })

@payments_bp.route('/mortgage/<int:mortgage_id>/payments', methods=['GET'])
@jwt_required()
def get_mortgage_payments(mortgage_id):
    """Get payment schedule for a mortgage"""
    payments = PaymentSchedule.query.filter_by(mortgage_id=mortgage_id).all()
    
    return jsonify([{
        'id': p.id,
        'payment_date': p.payment_date.isoformat(),
        'amount_due': p.amount_due,
        'amount_paid': p.amount_paid,
        'status': p.status.value
    } for p in payments])