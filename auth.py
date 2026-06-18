from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.models import db, User, Department
from services.notifications import notify_user, send_email_notification, generate_otp

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            phone = request.form.get('phone', '').strip()
            
            if not all([name, email, password]):
                flash('Name, email, and password are required!')
                return render_template('register.html')
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please login.')
                return render_template('register.html')
            
            role = 'user'  # default role
            hashed_password = generate_password_hash(password)
            
            user = User(name=name, email=email, password=hashed_password, phone=phone, role=role)
            db.session.add(user)
            db.session.commit()
            
            flash(f'Registration successful, {name}! Please login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}')
            return render_template('register.html')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Email and password required!')
                return render_template('login.html')
            
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash(f'Welcome {user.name}!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password!')
        except Exception as e:
            flash(f'Login error: {str(e)}')

    return render_template('login.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        try:
            code = request.form.get('otp', '').strip()
            pending_id = session.get('pending_user_id')
            otp_code = session.get('otp_code')
            expires = session.get('otp_expires')

            if not pending_id or not otp_code or not expires:
                flash('No OTP requested. Please login first.')
                return redirect(url_for('auth.login'))

            if datetime.utcnow() > datetime.fromisoformat(expires):
                flash('OTP expired. Please login again.')
                return redirect(url_for('auth.login'))

            if code == otp_code:
                user = User.query.get(pending_id)
                if user:
                    login_user(user)
                    session.pop('pending_user_id', None)
                    session.pop('otp_code', None)
                    session.pop('otp_expires', None)
                    flash('Login successful!')
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid OTP code!')
        except Exception as e:
            flash(f'OTP verification error: {str(e)}')

    return render_template('verify_otp.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))