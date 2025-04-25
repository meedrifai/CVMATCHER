# cv_matcher/app/routes/__init__.py
from flask import Blueprint

# Import routes
from .auth import auth
from .candidate import candidate_bp
from .recruiter import recruiter_bp
from .common import common_bp

def register_routes(app):
    """Register all blueprints/routes with the app."""
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(candidate_bp, url_prefix='/candidate')
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    app.register_blueprint(common_bp)