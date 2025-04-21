from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from ..services.auth_service import AuthService
from ..models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        if current_user.is_recruiter():
            return redirect(url_for('recruiter.dashboard'))
        else:
            return redirect(url_for('candidate.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Basic validation
        if not username or not email or not password or not role:
            flash('All fields are required')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('auth/register.html')
        
        # Register user
        success, message = AuthService.register_user(
            username, email, password, role, first_name, last_name
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        if current_user.is_recruiter():
            return redirect(url_for('recruiter.dashboard'))
        else:
            return redirect(url_for('candidate.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Authenticate user
        success, user = AuthService.authenticate_user(username, password)
        
        if success:
            # Log in user
            login_user(user, remember=remember)
            
            # Redirect based on role
            if user.is_recruiter():
                return redirect(url_for('recruiter.dashboard'))
            else:
                return redirect(url_for('candidate.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route."""
    if request.method == 'POST':
        # Update profile
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        
        try:
            from .. import db
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            from .. import db
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('auth/profile.html')

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        success, message = AuthService.change_password(
            current_user.id, current_password, new_password
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/change_password.html')