from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user
from flask_mail import Mail
import os
from models.models import db, User, Complaint, Notification, Upvote, Department
from routes.auth import auth_bp
from routes.complaints import complaints_bp
from routes.officer import officer_bp
from routes.admin import admin_bp
from scheduler.scheduler import start_scheduler


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a8f7s9df8s7df98s7df9s8df7s9df'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///civic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# 📧 Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jananikrishnamoorthi2006@gmail.com'
app.config['MAIL_PASSWORD'] = 'hqpglbapeecnueau'

db.init_app(app)
mail = Mail(app)

from services.notifications import set_mail
set_mail(mail)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==============================
# 🤖 SIMPLE AI LOGIC FUNCTIONS
# ==============================

def ai_assign_department(description):
    """Basic keyword-based AI department assignment"""
    description = description.lower()

    if "road" in description or "pothole" in description:
        return "Road Department", "road"
    elif "water" in description or "pipe" in description:
        return "Water Department", "water"
    elif "garbage" in description or "waste" in description:
        return "Sanitation Department", "garbage"
    elif "light" in description or "street light" in description:
        return "Electricity Department", "light"
    else:
        return "General Department", "general"


def ai_set_priority(description):
    """Simple AI priority detection"""
    description = description.lower()

    if any(word in description for word in ["urgent", "danger", "accident"]):
        return "high"
    elif any(word in description for word in ["delay", "issue"]):
        return "medium"
    else:
        return "low"


# ==============================
# 🔗 BLUEPRINTS
# ==============================

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(complaints_bp, url_prefix='/complaints')
app.register_blueprint(officer_bp, url_prefix='/officer')
app.register_blueprint(admin_bp, url_prefix='/admin')


# ==============================
# 📧 TEST EMAIL
# ==============================

@app.route('/test-email/<email>')
def test_email(email):
    from services.notifications import send_email_notification

    result = send_email_notification(
        email,
        'Test Email from Civic System',
        'This is a test email. If you received this, email is working!'
    )

    if result:
        return f'✓ Test email sent to {email}'
    else:
        return f'❌ Failed to send email'


# ==============================
# 🏠 HOME
# ==============================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


# ==============================
# 📊 USER DASHBOARD (UPDATED)
# ==============================

@app.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if current_user.role == 'user':
        complaints = Complaint.query.filter_by(user_id=current_user.id).all()
        all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

        notifications = Notification.query.filter_by(
            user_id=current_user.id, is_read=False
        ).all()

        notification_count = len(notifications)  # 🔔 bell count

        upvotes = {
            u.complaint_id: u
            for u in Upvote.query.filter_by(user_id=current_user.id).all()
        }

        # 🔥 Enhance complaints with AI display data
        for c in all_complaints:
            if not c.complaint_type or c.complaint_type == "general":
                dept_name, c.complaint_type = ai_assign_department(c.description)

                dept = Department.query.filter_by(name=dept_name).first()
                if dept:
                    c.department_id = dept.id

            if not c.priority:
                c.priority = ai_set_priority(c.description)

        db.session.commit()

        return render_template(
            'user_dashboard_modern.html',
            complaints=complaints,
            all_complaints=all_complaints,
            notifications=notifications,
            notification_count=notification_count,  # 🔔 NEW
            upvotes=upvotes
        )

    elif current_user.role == 'officer':
        return redirect(url_for('officer.dashboard'))

    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))


# ==============================
# 🚀 RUN APP
# ==============================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database ready")

    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler warning: {e}")

    print("\n✓ App running on http://localhost:5000\n")
    app.run(debug=True)