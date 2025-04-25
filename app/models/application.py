from datetime import datetime
from .. import db

class Application(db.Model):
    """Job application model for candidates applying to jobs."""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_offers.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resume_path = db.Column(db.String(255))
    resume_text = db.Column(db.Text)
    cover_letter = db.Column(db.Text)
    match_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'accepted', 'rejected'
    recruiter_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id}>'
    
    def to_dict(self):
        """Convert application to dictionary."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'applicant_id': self.applicant_id,
            'resume_path': self.resume_path,
            'resume_text': self.resume_text,
            'cover_letter': self.cover_letter,
            'match_percentage': self.match_percentage,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
