from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta 
from app.utils import momentjs
from lib.database import connect_db
import os
import hashlib

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.config')
app.config.from_pyfile('config.py', silent=True)

# Add ProxyFix middleware to handle reverse proxy headers (X-Forwarded-*)
# This enables proper URL generation when running behind a reverse proxy like haruka-tunnel
# Trust levels are configurable via PROXY_X_* environment variables in config.py
app.wsgi_app = ProxyFix(  # type: ignore[assignment]
    app.wsgi_app,
    x_for=app.config.get('PROXY_X_FOR', 1),
    x_proto=app.config.get('PROXY_X_PROTO', 1),
    x_host=app.config.get('PROXY_X_HOST', 1),
    x_prefix=app.config.get('PROXY_X_PREFIX', 1)
)

csrf = CSRFProtect(app)

if app.config['DATABASE_DEFAULT'] == 'postgres':
    connect_db('postgres', app)
elif app.config['DATABASE_DEFAULT'] == 'mysql':
    connect_db('mysql', app)
else:
    """ sqlite connection """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, app.config['DATABASE_NAME'])


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=120)
# Set jinja template global
app.jinja_env.globals['momentjs'] = momentjs

# Add md5 filter for Gravatar
@app.template_filter('md5')
def md5_filter(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

login = LoginManager(app)
login.login_view = 'login' # type: ignore[attr-defined]
login.refresh_view = 'relogin' # type: ignore[attr-defined]

login.needs_refresh_message = (u"Session timedout, please re-login")
login.needs_refresh_message_category = "info"

# Return JSON 401 for API requests, redirect for others
from flask import jsonify, request, url_for, redirect
@login.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login'))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    if db.engine.url.drivername == 'sqlite': # type: ignore[attr-defined]
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

# Register CLI commands
from app import cli
cli.create_cli(app)

from app import routes, models, utils

# Initialize default data when app starts (not during import)
_initialized = False

def initialize_default_data():
    """Initialize default data on first request, not during import"""
    global _initialized
    if _initialized:
        return
    
    try:
        # Check if tables exist before querying - use try/except for robustness
        try:
            user_count = models.User.query.count()
        except Exception:
            print("⚠️  User table not accessible, skipping data initialization")
            return
            
        try:
            status_count = models.Status.query.count()
        except Exception:
            print("⚠️  Status table not accessible, skipping data initialization")
            return

        # Check and seed users if none exist
        if user_count == 0:
            models.User.seed()

        # Always check and seed status records - be more robust
        if status_count == 0:
            models.Status.seed()
            db.session.commit()  # type: ignore[attr-defined]
        
        _initialized = True
        print("✅ Default data initialized successfully")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize default data: {e}")
        # Don't let this crash the app, but log the error
        import traceback
        traceback.print_exc()

@app.before_request
def ensure_initialized():
    """Ensure default data is initialized on first request"""
    initialize_default_data()


