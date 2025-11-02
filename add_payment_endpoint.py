#!/usr/bin/env python3

# Script to add payment endpoint to homebuyer routes

def add_payment_endpoint():
    with open('/home/ny4g4/Development/code/phase-5/Netlend-backened/routes/homebuyer.py', 'a') as f:
        f.write('''

@homebuyer_bp.route('/payments', methods=['POST'])
@jwt_required()
def process_payment():
    try:
        user_id = get_jwt_identity()
        if user_id.startswith('B'):
            buyer_id = int(user_id[1:])
        elif user_id.startswith('L'):
            buyer_id = int(user_id[1:])  # Use lender ID as buyer for testing
        else:
            buyer_id = int(user_id)
        
        data = request.json
        mortgage_id = data.get('mortgageId')
        amount = data.get('amount')
        payment_type = data.get('paymentType')
        
        from models import ActiveMortgage, PaymentSchedule, PaymentStatus
        
        # Verify mortgage ownership
        mortgage = ActiveMortgage.query.filter_by(id=mortgage_id, borrower_id=buyer_id).first()
        if not mortgage:
            return jsonify({'error': 'Mortgage not found'}), 404
        
        # Find the next pending payment
        next_payment = PaymentSchedule.query.filter_by(
            mortgage_id=mortgage_id,
            status=PaymentStatus.PENDING
        ).order_by(PaymentSchedule.payment_date).first()
        
        if next_payment:
            # Process the payment
            next_payment.amount_paid = amount
            next_payment.status = PaymentStatus.PAID
            
            # Update mortgage balance
            mortgage.remaining_balance -= amount
            
            # Update next payment due date
            next_pending = PaymentSchedule.query.filter_by(
                mortgage_id=mortgage_id,
                status=PaymentStatus.PENDING
            ).order_by(PaymentSchedule.payment_date).first()
            
            if next_pending:
                mortgage.next_payment_due = next_pending.payment_date
            else:
                # All payments completed
                mortgage.next_payment_due = None
                if mortgage.application and mortgage.application.listing:
                    from models import ListingStatus
                    mortgage.application.listing.status = ListingStatus.SOLD
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transactionId': f'TXN{int(datetime.now().timestamp() * 1000)}',
            'amount': amount,
            'paymentType': payment_type,
            'remainingBalance': mortgage.remaining_balance
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
''')
    print("✅ Added payment endpoint to homebuyer routes")

if __name__ == '__main__':
    add_payment_endpoint()