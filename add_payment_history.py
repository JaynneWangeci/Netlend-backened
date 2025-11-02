#!/usr/bin/env python3

# Script to add payment history endpoint to homebuyer routes

def add_payment_history_endpoint():
    with open('/home/ny4g4/Development/code/phase-5/Netlend-backened/routes/homebuyer.py', 'a') as f:
        f.write('''
@homebuyer_bp.route('/payments/<int:mortgage_id>', methods=['GET'])
@jwt_required()
def get_payment_history(mortgage_id):
    try:
        user_id = get_jwt_identity()
        if user_id.startswith('B'):
            buyer_id = int(user_id[1:])
        elif user_id.startswith('L'):
            buyer_id = int(user_id[1:])  # Use lender ID as buyer for testing
        else:
            buyer_id = int(user_id)
        
        from models import ActiveMortgage, PaymentSchedule
        mortgage = ActiveMortgage.query.filter_by(id=mortgage_id, borrower_id=buyer_id).first()
        
        if not mortgage:
            return jsonify({'error': 'Mortgage not found'}), 404
        
        payments = PaymentSchedule.query.filter_by(mortgage_id=mortgage_id).all()
        
        result = []
        for payment in payments:
            result.append({
                'id': payment.id,
                'date': payment.payment_date.isoformat(),
                'amountDue': payment.amount_due,
                'amountPaid': payment.amount_paid,
                'status': payment.status.value,
                'receiptUrl': payment.receipt_url
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
''')
    print("✅ Added payment history endpoint to homebuyer routes")

if __name__ == '__main__':
    add_payment_history_endpoint()