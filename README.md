# Smart Civic Grievance Management System

A web application for managing civic complaints with automatic department assignment, escalation, and notifications.

## Features

- User registration and authentication
- Complaint submission with image and GPS location
- Automatic department classification
- Officer dashboards for complaint management
- Admin panel for user and department management
- Escalation system for unresolved complaints
- Email and in-app notifications

## Setup Instructions

1. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Database Setup:**
   - Install PostgreSQL
   - Create a database named `civic_db`
   - Update the database URI in `app.py` with your credentials:
     ```
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/civic_db'
     ```
   - Run the schema:
     ```
     psql -d civic_db -f schema.sql
     ```

3. **Email Configuration:**
   - Update Flask-Mail settings in `app.py` with your email credentials.

4. **Run the Application:**
   ```
   python app.py
   ```

5. **Access the Application:**
   - Open http://localhost:5000 in your browser
   - Register as a user or login with admin credentials

## Folder Structure

```
civic-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # PostgreSQL database schema
├── models/
│   └── models.py         # SQLAlchemy models
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── complaints.py     # Complaint management routes
│   ├── officer.py        # Officer dashboard routes
│   └── admin.py          # Admin panel routes
├── services/
│   ├── classification.py # AI classification service
│   └── notifications.py  # Notification service
├── scheduler/
│   └── scheduler.py      # Background job scheduler
├── templates/            # HTML templates
├── static/               # CSS, JS, and uploaded images
└── README.md             # This file
```

## Usage

- **Users:** Register, submit complaints, view status, upvote others' complaints
- **Officers:** View assigned complaints, update status, add remarks and images
- **Admins:** Manage users, assign departments, view analytics

## Technologies Used

- Backend: Python Flask
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask-Login
- Email: Flask-Mail
- Scheduling: APScheduler