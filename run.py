# cv_matcher/run.py
import os
from app import create_app, db

# Get environment configuration
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Add database instance and models to flask shell context."""
    from app.models.user import User
    from app.models.job import Job
    from app.models.application import Application
    from app.models.notification import Notification
    
    return {
        'db': db, 
        'User': User, 
        'Job': Job, 
        'Application': Application, 
        'Notification': Notification
    }

if __name__ == '__main__':
    app.run()