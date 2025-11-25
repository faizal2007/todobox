from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from datetime import timedelta 
from app.utils import momentjs
from lib.database import connect_db
import os
import hashlib

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.config')
app.config.from_pyfile('config.py', silent=True)
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


