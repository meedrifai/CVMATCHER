from ..models.notification import Notification
from ..models.user import User
from .. import db

class NotificationService:
    """Service for notification operations."""
    
    @staticmethod
    def create_notification(user_id, message, link=None):
        """Create a new notification for a user."""
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            message=message,
            link=link
        )
        
        try:
            # Save to database
            db.session.add(notification)
            db.session.commit()
            return True, "Notification created successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating notification: {str(e)}"
    
    @staticmethod
    def get_user_notifications(user_id, include_read=False):
        """Get notifications for a user."""
        query = Notification.query.filter_by(user_id=user_id)
        
        if not include_read:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """Mark a notification as read."""
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return False, "Notification not found"
        
        notification.is_read = True
        
        try:
            db.session.commit()
            return True, "Notification marked as read"
        except Exception as e:
            db.session.rollback()
            return False, f"Error marking notification as read: {str(e)}"
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all user notifications as read."""
        try:
            Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
            db.session.commit()
            return True, "All notifications marked as read"
        except Exception as e:
            db.session.rollback()
            return False, f"Error marking notifications as read: {str(e)}"
    
    @staticmethod
    def notify_application_status_change(application_id, new_status):
        """Create notification for application status change."""
        from ..models.application import Application
        
        application = Application.query.get(application_id)
        if not application:
            return False, "Application not found"
        
        # Get job title
        job_title = application.job.title
        
        # Create notification message
        message = f"Your application for '{job_title}' has been {new_status}"
        
        # Create link to application details
        link = f"/candidate/applications/{application_id}"
        
        # Create notification
        return NotificationService.create_notification(
            application.applicant_id,
            message,
            link
        )
    
    @staticmethod
    def notify_new_application(application_id):
        """Create notification for new application."""
        from ..models.application import Application
        
        application = Application.query.get(application_id)
        if not application:
            return False, "Application not found"
        
        # Get candidate name
        candidate = User.query.get(application.applicant_id)
        candidate_name = f"{candidate.first_name} {candidate.last_name}" if candidate.first_name else candidate.username
        
        # Get job title
        job_title = application.job.title
        
        # Create notification message
        message = f"New application from {candidate_name} for '{job_title}'"
        
        # Create link to application details
        link = f"/recruiter/applications/{application_id}"
        
        # Create notification
        return NotificationService.create_notification(
            application.job.creator_id,
            message,
            link
        )