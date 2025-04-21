from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from ..models.job import Job
from ..models.application import Application
from ..services.cv_matching_service import CVMatchingService

recruiter = Blueprint('recruiter', __name__)

@recruiter.route('/dashboard')
@login_required
def dashboard():
    """Recruiter dashboard route."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get recruiter's jobs
    jobs = Job.query.filter_by(recruiter_id=current_user.id).all()
    
    # Get applications count for each job
    job_stats = {}
    for job in jobs:
        applications_count = Application.query.filter_by(job_id=job.id).count()
        job_stats[job.id] = {
            'applications_count': applications_count
        }
    
    return render_template(
        'recruiter/dashboard.html',
        jobs=jobs,
        job_stats=job_stats
    )

@recruiter.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    """Post new job route."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        salary_range = request.form.get('salary_range')
        
        # Basic validation
        if not title or not description or not requirements:
            flash('Title, description and requirements are required', 'danger')
            return render_template('recruiter/post_job.html')
        
        # Create new job
        job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
            recruiter_id=current_user.id,
            is_active=True
        )
        
        try:
            from .. import db
            db.session.add(job)
            db.session.commit()
            flash('Job posted successfully', 'success')
            return redirect(url_for('recruiter.dashboard'))
        except Exception as e:
            from .. import db
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')
    
    return render_template('recruiter/post_job.html')

@recruiter.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit job route."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get job
    job = Job.query.get_or_404(job_id)
    
    # Ensure job belongs to recruiter
    if job.recruiter_id != current_user.id:
        flash('Access denied. You can only edit your own jobs.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.location = request.form.get('location')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.salary_range = request.form.get('salary_range')
        job.is_active = True if request.form.get('is_active') else False
        
        try:
            from .. import db
            db.session.commit()
            flash('Job updated successfully', 'success')
            return redirect(url_for('recruiter.dashboard'))
        except Exception as e:
            from .. import db
            db.session.rollback()
            flash(f'Error updating job: {str(e)}', 'danger')
    
    return render_template('recruiter/edit_job.html', job=job)

@recruiter.route('/jobs/<int:job_id>/applications')
@login_required
def view_applications(job_id):
    """View job applications route."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get job
    job = Job.query.get_or_404(job_id)
    
    # Ensure job belongs to recruiter
    if job.recruiter_id != current_user.id:
        flash('Access denied. You can only view applications for your own jobs.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
    
    # Get applications
    applications = Application.query.filter_by(job_id=job_id).all()
    
    # Get matching scores
    application_scores = {}
    for application in applications:
        score = CVMatchingService.get_matching_score(application.candidate_id, job_id)
        application_scores[application.id] = score
    
    return render_template(
        'recruiter/applications.html',
        job=job,
        applications=applications,
        application_scores=application_scores
    )

@recruiter.route('/applications/<int:application_id>/update-status', methods=['POST'])
@login_required
def update_application_status(application_id):
    """Update application status route."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get application
    application = Application.query.get_or_404(application_id)
    
    # Get job to ensure it belongs to recruiter
    job = Job.query.get_or_404(application.job_id)
    
    # Ensure job belongs to recruiter
    if job.recruiter_id != current_user.id:
        flash('Access denied. You can only update applications for your own jobs.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
    
    # Update status
    new_status = request.form.get('status')
    if new_status in ['PENDING', 'REVIEWING', 'REJECTED', 'SHORTLISTED', 'INTERVIEW', 'OFFERED', 'ACCEPTED']:
        application.status = new_status
        
        try:
            from .. import db
            db.session.commit()
            
            # Create notification for candidate
            from ..models.notification import Notification
            from ..services.notification_service import NotificationService
            
            message = f"Your application for {job.title} has been updated to {new_status}."
            NotificationService.create_notification(
                application.candidate_id,
                message,
                f"application:{application.id}"
            )
            
            flash('Application status updated successfully', 'success')
        except Exception as e:
            from .. import db
            db.session.rollback()
            flash(f'Error updating application status: {str(e)}', 'danger')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('recruiter.view_applications', job_id=application.job_id))

@recruiter.route('/jobs/<int:job_id>/toggle-status', methods=['POST'])
@login_required
def toggle_job_status(job_id):
    """Toggle job active status."""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get job
    job = Job.query.get_or_404(job_id)
    
    # Ensure job belongs to recruiter
    if job.recruiter_id != current_user.id:
        flash('Access denied. You can only update your own jobs.', 'danger')
        return redirect(url_for('recruiter.dashboard'))
    
    # Toggle status
    job.is_active = not job.is_active
    
    try:
        from .. import db
        db.session.commit()
        
        status = "activated" if job.is_active else "deactivated"
        flash(f'Job {status} successfully', 'success')
    except Exception as e:
        from .. import db
        db.session.rollback()
        flash(f'Error updating job status: {str(e)}', 'danger')
    
    return redirect(url_for('recruiter.dashboard'))