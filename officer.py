from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from models.models import db, Complaint, Update
from services.notifications import notify_user

officer_bp = Blueprint('officer', __name__)

@officer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'officer':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))

    complaints = Complaint.query.filter_by(department_id=current_user.department_id).all()
    status_filter = request.args.get('status')
    if status_filter:
        complaints = [c for c in complaints if c.status == status_filter]

    return render_template('officer_dashboard.html', complaints=complaints)

@officer_bp.route('/update/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def update_complaint(complaint_id):
    if current_user.role != 'officer':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))

    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.department_id != current_user.department_id:
        flash('Access denied')
        return redirect(url_for('officer.dashboard'))

    if request.method == 'POST':
        status = request.form['status']
        remarks = request.form['remarks']

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', filename)
                file.save(filepath)
                image_path = f'uploads/{filename}'

        # Update complaint status
        complaint.status = status
        update = Update(
            complaint_id=complaint_id,
            officer_id=current_user.id,
            status=status,
            remarks=remarks,
            image_path=image_path
        )
        db.session.add(update)
        db.session.commit()

        # Notify user
        user = complaint.user
        notify_user(user, f"Your complaint status updated to {status}. Remarks: {remarks}")

        flash('Complaint updated successfully!')
        return redirect(url_for('officer.dashboard'))

    return render_template('update_complaint.html', complaint=complaint)