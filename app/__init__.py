from flask import Blueprint, Flask
from .extensions import db, login_manager
from flask_migrate import Migrate

from .config import config

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__,template_folder='templates')
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    main = Blueprint('main', __name__, template_folder='templates')
    # Register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main, url_prefix='/')
    
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes.candidate import candidate_bp as candidate_blueprint 
    app.register_blueprint(candidate_blueprint)
    
    from .routes.recruiter import recruiter_bp as recruiter_blueprint
    app.register_blueprint(recruiter_blueprint)
    
    from .routes.common import common_bp as common_blueprint
    app.register_blueprint(common_blueprint)
    
    # Create upload folder if it doesn't exist
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app
