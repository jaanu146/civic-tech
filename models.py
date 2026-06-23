from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#2563eb')  # Badge color
    icon = db.Column(db.String(50), default='🏢')  # Icon

    users = db.relationship('User', backref='department', lazy=True)
    complaints = db.relationship('Complaint', backref='department', lazy=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)  # user, officer, admin
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship('Complaint', backref='user', lazy=True)
    upvotes = db.relationship('Upvote', backref='user', lazy=True)
    updates = db.relationship('Update', backref='officer', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))

    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    status = db.Column(db.String(20), default='pending')  # pending, in_progress, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)

    escalation_level = db.Column(db.Integer, default=1)

    # 🤖 AI-related fields
    ai_assigned = db.Column(db.Boolean, default=True)
    
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    complaint_type = db.Column(db.String(50), default='general')  # road, water, garbage, light

    upvotes = db.relationship('Upvote', backref='complaint', lazy=True)
    updates = db.relationship('Update', backref='complaint', lazy=True)
    escalations = db.relationship('Escalation', backref='complaint', lazy=True)

    # ✅ 🔴 Priority Color Helper (for UI)
    def get_priority_color(self):
        return {
            'high': 'red',
            'medium': 'orange',
            'low': 'green'
        }.get(self.priority, 'gray')

    # ✅ 📊 Escalation Step Indicator
    def get_escalation_steps(self):
        steps = []
        for i in range(1, 4):  # 3 levels
            steps.append({
                "level": i,
                "active": i <= self.escalation_level
            })
        return steps

    # ✅ 📅 Timeline Generator (for UI timeline)
    @property
    def timeline(self):
        events = []

        # Complaint Created
        events.append({
            "title": "Complaint Registered",
            "time": self.created_at
        })

        # Updates Timeline
        for update in self.updates:
            events.append({
                "title": f"Status changed to {update.status}",
                "time": update.updated_at
            })

        # Escalations Timeline
        for esc in self.escalations:
            events.append({
                "title": f"Escalated to Level {esc.to_level}",
                "time": esc.escalated_at
            })

        # Sort by time
        events.sort(key=lambda x: x["time"])

        return events


class Upvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'complaint_id'),)


class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    status = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text)
    image_path = db.Column(db.String(255))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Escalation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)

    from_level = db.Column(db.Integer, nullable=False)
    to_level = db.Column(db.Integer, nullable=False)

    escalated_at = db.Column(db.DateTime, default=datetime.utcnow)