from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from models.models import db, Complaint, Department, Upvote, Update
from services.classification import classify_department
from services.notifications import notify_user
from datetime import datetime, timedelta

complaints_bp = Blueprint('complaints', __name__)

def classify_complaint_type(description):
    """AI function to classify complaint type based on description"""
    description_lower = description.lower()
    
    # Road/Street related keywords
    if any(word in description_lower for word in ['road', 'street', 'pothole', 'pavement', 'highway', 'lane', 'asphalt', 'damaged road', 'broken road']):
        return 'road'
    
    # Water related keywords
    elif any(word in description_lower for word in ['water', 'pipe', 'leak', 'plumbing', 'water supply', 'drainage', 'sewage', 'water line']):
        return 'water'
    
    # Garbage/Sanitation related keywords
    elif any(word in description_lower for word in ['garbage', 'waste', 'trash', 'dump', 'litter', 'sanitation', 'cleaning', 'dirty']):
        return 'garbage'
    
    # Light/Street lighting related keywords
    elif any(word in description_lower for word in ['light', 'street light', 'electricity', 'bulb', 'dark', 'lighting', 'electrical']):
        return 'light'
    
    # Health related keywords
    elif any(word in description_lower for word in ['health', 'hospital', 'clinic', 'disease', 'medical', 'hygiene', 'health center']):
        return 'health'
    
    # Safety related keywords
    elif any(word in description_lower for word in ['safety', 'crime', 'theft', 'assault', 'accident', 'emergency', 'danger', 'police']):
        return 'safety'
    
    return 'general'

def determine_priority(description, complaint_type, upvotes_count=0):
    """AI function to determine priority level based on description and upvotes"""
    description_lower = description.lower()
    
    # Keywords for high priority
    high_priority_keywords = ['urgent', 'critical', 'emergency', 'serious', 'danger', 'hazard', 'accident', 'injury', 'death']
    
    # Keywords for medium priority
    medium_priority_keywords = ['important', 'significant', 'needs attention', 'issue', 'problem', 'broken']
    
    # Check for high priority keywords
    if any(word in description_lower for word in high_priority_keywords):
        return 'high'
    
    # Check for medium priority keywords
    if any(word in description_lower for word in medium_priority_keywords):
        return 'medium'
    
    # Check upvotes - high upvotes indicate community concern
    if upvotes_count >= 5:
        return 'high'
    elif upvotes_count >= 2:
        return 'medium'
    
    # Safety and Health are generally high priority
    if complaint_type in ['safety', 'health']:
        return 'high'
    
    # Road issues are medium priority
    if complaint_type in ['road', 'water']:
        return 'medium'
    
    return 'low'

@complaints_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        description = request.form['description']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # AI: Classify complaint type
        complaint_type = classify_complaint_type(description)
        
        # AI: Determine priority
        priority = determine_priority(description, complaint_type)

        # Classify department
        dept_name = classify_department(description)
        department = Department.query.filter_by(name=dept_name).first()

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', filename)
                file.save(filepath)
                image_path = f'uploads/{filename}'

        # Create complaint with AI-powered fields
        deadline = datetime.utcnow() + timedelta(days=7)  # 7 days deadline
        complaint = Complaint(
            user_id=current_user.id,
            description=description,
            image_path=image_path,
            latitude=latitude,
            longitude=longitude,
            department_id=department.id if department else None,
            deadline=deadline,
            ai_assigned=True,  # AI assigned this complaint
            priority=priority,  # AI-determined priority
            complaint_type=complaint_type  # AI-classified type
        )
        db.session.add(complaint)
        db.session.commit()

        # Notify user with AI info
        priority_text = f"Priority: {priority.upper()}"
        notify_user(current_user, f"Your complaint has been submitted and assigned to {dept_name}. {priority_text}")

        flash('Complaint submitted successfully!')
        return redirect(url_for('dashboard'))

    return render_template('submit_complaint.html')

@complaints_bp.route('/view/<int:complaint_id>')
@login_required
def view(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.user_id != current_user.id and current_user.role not in ['officer', 'admin']:
        flash('Access denied')
        return redirect(url_for('dashboard'))

    updates = Update.query.filter_by(complaint_id=complaint_id).order_by(Update.updated_at).all()
    return render_template('view_complaint.html', complaint=complaint, updates=updates)

@complaints_bp.route('/upvote/<int:complaint_id>', methods=['POST'])
@login_required
def upvote(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    existing_upvote = Upvote.query.filter_by(user_id=current_user.id, complaint_id=complaint_id).first()
    if existing_upvote:
        flash('You have already upvoted this complaint.')
    else:
        upvote = Upvote(user_id=current_user.id, complaint_id=complaint_id)
        db.session.add(upvote)
        
        # AI: Update priority based on upvotes
        upvote_count = len(complaint.upvotes) + 1
        new_priority = determine_priority(complaint.description, complaint.complaint_type, upvote_count)
        complaint.priority = new_priority
        
        db.session.commit()
        flash('Upvoted successfully!')

    return redirect(url_for('dashboard'))