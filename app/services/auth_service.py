from flask import current_app
from ..models.user import User
from .. import db

class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def register_user(username, email, password, role, first_name=None, last_name=None):
        """Register a new user."""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return False, "Username already exists"
        
        if User.query.filter_by(email=email).first():
            return False, "Email already exists"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        try:
            # Add user to database
            db.session.add(user)
            db.session.commit()
            return True, "User registered successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error registering user: {str(e)}"
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user."""
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            return True, user
        
        return False, None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password."""
        user = User.query.get(user_id)
        
        if not user:
            return False, "User not found"
        
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        user.set_password(new_password)
        
        try:
            db.session.commit()
            return True, "Password changed successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error changing password: {str(e)}"