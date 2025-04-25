from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..services.cv_matching_service import CVMatchingService
from ..models.job import JobOffer
from ..models.application import Application
import os
import uuid

# ✅ Utiliser le même nom dans les décorateurs
candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))

    applications = current_user.applications
    return render_template('candidate/dashboard.html', applications=applications)

@candidate_bp.route('/job-listings')
@login_required
def job_listings():
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))

    jobs = JobOffer.query.filter_by(is_active=True).all()

    resume_file = None
    if current_user.resume_path:
        resume_file = os.path.basename(current_user.resume_path)

    job_matches = {}
    if current_user.resume_path:
        for job in jobs:
            score = CVMatchingService.get_matching_score(current_user.id, job.id)
            job_matches[job.id] = score

    return render_template(
        'candidate/job_listings.html',
        jobs=jobs,
        job_matches=job_matches,
        resume_file=resume_file
    )

@candidate_bp.route('/upload-resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            current_user.resume_path = file_path

            try:
                from .. import db
                db.session.commit()
                flash('Resume uploaded successfully', 'success')
                CVMatchingService.process_resume(current_user.id, file_path)
                return redirect(url_for('candidate.dashboard'))
            except Exception as e:
                from .. import db
                db.session.rollback()
                flash(f'Error uploading resume: {str(e)}', 'danger')

    return render_template('candidate/upload_resume.html')

@candidate_bp.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))

    job = JobOffer.query.get_or_404(job_id)

    existing_application = Application.query.filter_by(
        candidate_id=current_user.id,
        job_id=job_id
    ).first()

    if existing_application:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('candidate.job_listings'))

    if not current_user.resume_path:
        flash('Please upload your resume first', 'warning')
        return redirect(url_for('candidate.upload_resume'))

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '')
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

    matching_score = CVMatchingService.get_matching_score(current_user.id, job_id)

    return render_template(
        'candidate/apply_job.html',
        job=job,
        matching_score=matching_score
    )

@candidate_bp.route('/applications')
@login_required
def view_applications():
    if not current_user.is_candidate():
        flash('Access denied. Candidate role required.', 'danger')
        return redirect(url_for('common.index'))

    applications = Application.query.filter_by(candidate_id=current_user.id).all()
    return render_template('candidate/applications.html', applications=applications)
