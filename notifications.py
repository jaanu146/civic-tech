from flask_mail import Message
from models.models import db, Notification
import random

mail = None

def set_mail(m):
    global mail
    mail = m

def generate_otp(length=6):
    """Generate a numeric OTP code."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(user_email, otp, validity_minutes=10):
    """Send an OTP message via email."""
    subject = 'Your Civic Grievance System OTP'
    body = f'Your OTP is {otp}. It is valid for {validity_minutes} minutes.'
    send_email_notification(user_email, subject, body)

def send_email_notification(user_email, subject, body):
    """
    Send email notification using Flask-Mail.
    """
    if not mail:
        print(f"⚠️  Mail not configured. Email to {user_email} not sent.")
        return False
    
    try:
        msg = Message(subject, recipients=[user_email])
        msg.body = body
        mail.send(msg)
        print(f"✓ Email sent to {user_email}: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email sending FAILED to {user_email}")
        print(f"   Error: {str(e)}")
        print(f"   Subject: {subject}")
        return False

def create_db_notification(user_id, message):
    """
    Create a notification in the database.
    """
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()

def notify_user(user, message):
    """
    Notify user via database and email.
    """
    create_db_notification(user.id, message)
    send_email_notification(user.email, "Civic Grievance Update", message)