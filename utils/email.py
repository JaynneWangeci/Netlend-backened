from flask_mail import Message
from app import mail
import os

def send_verification_email(email, user_id):
    msg = Message(
        'Verify Your NetLend Account',
        recipients=[email]
    )
    
    verification_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify/{user_id}"
    
    msg.html = f"""
    <h2>Welcome to NetLend!</h2>
    <p>Please click the link below to verify your email address:</p>
    <a href="{verification_url}">Verify Email</a>
    <p>If you didn't create this account, please ignore this email.</p>
    """
    
    mail.send(msg)

