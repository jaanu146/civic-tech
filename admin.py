from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models.models import db, User, Department, Complaint

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))

    users = User.query.all()
    departments = Department.query.all()
    complaints = Complaint.query.all()

    # Basic analytics
    total_complaints = len(complaints)
    resolved_complaints = len([c for c in complaints if c.status == 'resolved'])
    pending_complaints = len([c for c in complaints if c.status == 'pending'])

    return render_template('admin_dashboard.html', users=users, departments=departments,
                         total_complaints=total_complaints, resolved_complaints=resolved_complaints,
                         pending_complaints=pending_complaints)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']
        department_id = request.form.get('department_id') if role == 'officer' else None

        hashed_password = generate_password_hash(password, method='bcrypt')

        user = User(name=name, email=email, password=hashed_password, phone=phone, role=role, department_id=department_id)
        db.session.add(user)
        db.session.commit()

        flash('User added successfully!')
        return redirect(url_for('admin.dashboard'))

    departments = Department.query.all()
    return render_template('add_user.html', departments=departments)

@admin_bp.route('/assign_department/<int:user_id>', methods=['POST'])
@login_required
def assign_department(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    department_id = request.form['department_id']
    user.department_id = department_id
    db.session.commit()

    flash('Department assigned successfully!')
    return redirect(url_for('admin.dashboard'))