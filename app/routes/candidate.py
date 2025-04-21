from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..services.cv_matching_service import CVMatchingService
from ..models.job import Job
from ..models.application import Application
import os
import uuid

candidate = Blueprint('candidate', __name__)

@candidate.route('/dashboard')
@login_required
def dashboard():
    """Candidate dashboard route."""
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get candidate's applications
    applications = Application.query.filter_by(candidate_id=current_user.id).all()
    
    return render_template(
        'candidate/dashboard.html', 
        applications=applications
    )

@candidate.route('/job-listings')
@login_required
def job_listings():
    """Job listings route for candidates."""
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get all active jobs
    jobs = Job.query.filter_by(is_active=True).all()
    
    # Get candidate's resume information if available
    resume_file = None
    if current_user.resume_path:
        resume_file = os.path.basename(current_user.resume_path)
    
    # Get matching scores if resume is uploaded
    job_matches = {}
    if current_user.resume_path:
        # Get matching scores for each job
        for job in jobs:
            score = CVMatchingService.get_matching_score(current_user.id, job.id)
            job_matches[job.id] = score
    
    return render_template(
        'candidate/job_listings.html',
        jobs=jobs,
        job_matches=job_matches,
        resume_file=resume_file
    )

@candidate.route('/upload-resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload resume route."""
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['resume']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Update user's resume path
            current_user.resume_path = file_path
            
            try:
                from .. import db
                db.session.commit()
                flash('Resume uploaded successfully', 'success')
                
                # Process resume for matching
                CVMatchingService.process_resume(current_user.id, file_path)
                
                return redirect(url_for('candidate.dashboard'))
            except Exception as e:
                from .. import db
                db.session.rollback()
                flash(f'Error uploading resume: {str(e)}', 'danger')
    
    return render_template('candidate/upload_resume.html')

@candidate.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    """Apply for job route."""
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))
    
    # Check if job exists
    job = Job.query.get_or_404(job_id)
    
    # Check if user has already applied
    existing_application = Application.query.filter_by(
        candidate_id=current_user.id,
        job_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('candidate.job_listings'))
    
    # Check if user has uploaded resume
    if not current_user.resume_path:
        flash('Please upload your resume first', 'warning')
        return redirect(url_for('candidate.upload_resume'))
    
    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '')
        
        # Create new application
        application = Application(
            candidate_id=current_user.id,
            job_id=job_id,
            cover_letter=cover_letter,
            status='PENDING'
        )
        
        try:
            from .. import db
            db.session.add(application)
            db.session.commit()
            flash('Application submitted successfully', 'success')
            return redirect(url_for('candidate.dashboard'))
        except Exception as e:
            from .. import db
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'danger')
    
    # Get matching score
    matching_score = CVMatchingService.get_matching_score(current_user.id, job_id)
    
    return render_template(
        'candidate/apply_job.html',
        job=job,
        matching_score=matching_score
    )

@candidate.route('/applications')
@login_required
def view_applications():
    """View candidate's applications."""
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))
    
    applications = Application.query.filter_by(candidate_id=current_user.id).all()
    
    return render_template(
        'candidate/applications.html',
        applications=applications
    )