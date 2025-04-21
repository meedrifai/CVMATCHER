import os
from flask import current_app
from werkzeug.utils import secure_filename
import uuid
from ..models.application import Application
from ..models.job import JobOffer
from ..models.user import User
from ..ai.cv_matcher import CVMatcher
from .. import db

class CVMatchingService:
    """Service for CV matching operations."""
    
    def __init__(self):
        self.cv_matcher = CVMatcher()
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'models', 'cv_matcher_model.pkl'
        )
        # Try to load pre-trained model
        self.cv_matcher.load_model(model_path)
    
    def extract_text_from_resume(self, file_path):
        """Extract text from resume file."""
        # In a real implementation, we would handle different file types
        # (PDF, DOCX, etc.) using appropriate libraries
        
        # For simplicity, we'll just read the file as text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting text from resume: {e}")
            return ""
    
    def save_resume(self, file):
        """Save uploaded resume file."""
        if not file:
            return None, "No file provided"
        
        # Create a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            # Save the file
            file.save(file_path)
            return file_path, None
        except Exception as e:
            return None, f"Error saving resume: {str(e)}"
    
    def process_application(self, job_id, applicant_id, resume_file, cover_letter=None):
        """Process a job application with CV matching."""
        # Check if job exists
        job = JobOffer.query.get(job_id)
        if not job:
            return False, "Job not found", None
        
        # Check if user exists
        user = User.query.get(applicant_id)
        if not user or not user.is_candidate():
            return False, "Invalid applicant", None
        
        # Save resume
        resume_path, error = self.save_resume(resume_file)
        if error:
            return False, error, None
        
        # Extract text from resume
        resume_text = self.extract_text_from_resume(resume_path)
        
        # Calculate match percentage
        match_percentage = self.cv_matcher.predict_match(resume_text, job.description) * 100
        
        # Create application record
        application = Application(
            job_id=job_id,
            applicant_id=applicant_id,
            resume_path=resume_path,
            resume_text=resume_text,
            cover_letter=cover_letter,
            match_percentage=match_percentage,
            status='pending'
        )
        
        try:
            # Save to database
            db.session.add(application)
            db.session.commit()
            return True, "Application submitted successfully", application
        except Exception as e:
            db.session.rollback()
            return False, f"Error submitting application: {str(e)}", None
    
    def get_matched_applications(self, job_id, min_match_percentage=0):
        """Get applications for a job with match percentage above threshold."""
        return Application.query.filter(
            Application.job_id == job_id,
            Application.match_percentage >= min_match_percentage
        ).order_by(Application.match_percentage.desc()).all()
    
    def update_application_status(self, application_id, new_status, recruiter_notes=None):
        """Update application status."""
        application = Application.query.get(application_id)
        
        if not application:
            return False, "Application not found"
        
        application.status = new_status
        if recruiter_notes:
            application.recruiter_notes = recruiter_notes
        
        try:
            db.session.commit()
            return True, f"Application status updated to {new_status}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating application status: {str(e)}"