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
import logging

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
    return hashlib.md5(text.encode('utf-8')).hexdigest()  # nosec - Used only for Gravatar avatar generation, not for security

# Add markdown filter to render markdown as HTML
@app.template_filter('render_markdown')
def render_markdown(text):
    """Render markdown text to HTML"""
    import markdown
    from bleach import clean
    
    if not text:
        return ''
    
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'pymdownx.tilde'])
    
    # Sanitize HTML to allow safe tags
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'hr',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'del', 's', 'strike'
    ]
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
        'code': ['class'],
        'pre': ['class']
    }
    
    return clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=False)

# Add cache-busting headers for static files in development
@app.after_request
def add_security_headers(response):
    """Add security headers and cache-busting headers"""
    # Cache control for development and production
    if app.debug:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    else:
        # Production cache control - no caching for dynamic content
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (basic but secure)
    if not app.debug:
        # Allow required third-party CDNs (Flatpickr assets). Keep list minimal for security.
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://static.cloudflareinsights.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://maxcdn.bootstrapcdn.com; "
            "img-src 'self' https://cdn.jsdelivr.net https://*.geekdo.me https://www.gravatar.com data:; "
            "connect-src 'self'; "
            "font-src 'self' data: https://cdn.jsdelivr.net https://fonts.gstatic.com https://maxcdn.bootstrapcdn.com; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
    
    return response

login = LoginManager(app)
login.login_view = 'login' # type: ignore[attr-defined]
login.refresh_view = 'relogin' # type: ignore[attr-defined]

login.needs_refresh_message = (u"Session timedout, please re-login")
login.needs_refresh_message_category = "info"

# Return JSON 401 for API requests, redirect for others
from flask import jsonify, request, url_for, redirect, send_from_directory
@login.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login'))

# Disable all caching for mobile - all requests go directly online
@app.before_request
def disable_cache():
    """Disable caching on all responses to ensure direct online queries"""
    pass

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

# Serve service worker at root scope
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

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
            logging.warning("⚠️  User table not accessible, skipping data initialization")
            return
            
        try:
            status_count = models.Status.query.count()
        except Exception:
            logging.warning("⚠️  Status table not accessible, skipping data initialization")
            return

        # Check and seed users if none exist
        # DISABLED: User creation moved to frontend setup
        # if user_count == 0:
        #     models.User.seed()

        # Always check and seed status records - be more robust
        if status_count == 0:
            models.Status.seed()
            db.session.commit()  # type: ignore[attr-defined]
        
        _initialized = True
        logging.info("✅ Default data initialized successfully")
        
    except Exception as e:
        # Use logging.exception to include traceback in logs
        logging.exception("Failed to initialize default data")

@app.before_request
def ensure_initialized():
    """Ensure default data is initialized on first request"""
    initialize_default_data()


@app.route('/healthz')
def healthz():
    """Liveness/health endpoint for monitors and Cloudflare checks."""
    try:
        # Simple DB check: execute lightweight query if DB is configured
        # For sqlite, this is fast; for other DBs, still minimal
        db.session.execute('SELECT 1')  # type: ignore[attr-defined]
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        # Avoid leaking internal details; log server-side if needed
        return jsonify({"status": "error"}), 500


