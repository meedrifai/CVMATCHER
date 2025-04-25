from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models.notification import Notification

common_bp = Blueprint('common', __name__)

@common_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_recruiter():
            return redirect(url_for('recruiter.dashboard'))
        elif current_user.is_candidate():
            return redirect(url_for('candidate.dashboard'))
    return render_template('index.html')

@common_bp.route('/notifications')
@login_required
def notifications():
    """User notifications route."""
    # Get user notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template(
        'common/notifications.html',
        notifications=notifications
    )

@common_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read."""
    # Get notification
    notification = Notification.query.get_or_404(notification_id)
    
    # Ensure notification belongs to user
    if notification.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('common.notifications'))
    
    # Mark as read
    notification.is_read = True
    
    try:
        from .. import db
        db.session.commit()
    except Exception as e:
        from .. import db
        db.session.rollback()
        flash(f'Error marking notification as read: {str(e)}', 'danger')
    
    return redirect(url_for('common.notifications'))

@common_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    try:
        from .. import db
        # Get all unread notifications for user
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        # Mark all as read
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        flash('All notifications marked as read', 'success')
    except Exception as e:
        from .. import db
        db.session.rollback()
        flash(f'Error marking notifications as read: {str(e)}', 'danger')
    
    return redirect(url_for('common.notifications'))

@common_bp.route('/about')
def about():
    """About page route."""
    return render_template('common/about.html')

@common_bp.route('/contact')
def contact():
    """Contact page route."""
    return render_template('common/contact.html')

@common_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page route."""
    return render_template('common/privacy_policy.html')

@common_bp.route('/terms-of-service')
def terms_of_service():
    """Terms of service page route."""
    return render_template('common/terms_of_service.html')