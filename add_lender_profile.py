# Add these endpoints to routes/lender.py

@lender_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_lender_profile():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    lender = Lender.query.get(lender_id)
    
    return jsonify({
        'id': lender.id,
        'institution_name': lender.institution_name,
        'contact_person': lender.contact_person,
        'email': lender.email,
        'phone_number': lender.phone_number,
        'business_registration_number': lender.business_registration_number,
        'verified': lender.verified,
        'logo_url': lender.logo_url
    })

@lender_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_lender_profile():
    user_id = get_jwt_identity()
    lender_id = int(user_id[1:]) if user_id.startswith('L') else int(user_id)
    lender = Lender.query.get(lender_id)
    data = request.json
    
    if 'company_name' in data:
        lender.institution_name = data['company_name']
    if 'contact_person' in data:
        lender.contact_person = data['contact_person']
    if 'contact_email' in data:
        lender.email = data['contact_email']
    if 'phone' in data:
        lender.phone_number = data['phone']
    if 'license_number' in data:
        lender.business_registration_number = data['license_number']
    if 'logo_url' in data:
        lender.logo_url = data['logo_url']
    
    db.session.commit()
    return jsonify({'success': True})