from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models.models import db, Complaint, Escalation, User
from services.notifications import notify_user

def check_escalations():
    """
    Check for complaints that need escalation.
    """
    try:
        with db.session.begin():
            overdue_complaints = Complaint.query.filter(
                Complaint.deadline < datetime.utcnow(),
                Complaint.status != 'resolved'
            ).all()

            for complaint in overdue_complaints:
                if complaint.escalation_level < 3:  # max level 3
                    new_level = complaint.escalation_level + 1
                    escalation = Escalation(
                        complaint_id=complaint.id,
                        from_level=complaint.escalation_level,
                        to_level=new_level
                    )
                    complaint.escalation_level = new_level
                    complaint.deadline = datetime.utcnow() + timedelta(days=7)
                    db.session.add(escalation)

                    user = complaint.user
                    message = f"Your complaint '{complaint.description[:50]}...' has been escalated to level {new_level}."
                    notify_user(user, message)

                    officers = User.query.filter_by(department_id=complaint.department_id, role='officer').all()
                    for officer in officers:
                        notify_user(officer, f"Complaint escalated to level {new_level}: {complaint.description[:50]}...")
    except Exception as e:
        print(f"Escalation check error: {e}")

def start_scheduler():
    """
    Start the background scheduler.
    """
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=check_escalations, trigger="interval", hours=24)
        scheduler.start()
        print("Background scheduler started successfully!")
    except Exception as e:
        print(f"Scheduler error: {e}")