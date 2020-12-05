from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from app.utils import momentjs

import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('app.config')
app.config.from_pyfile('config.py', silent=True)
csrf = CSRFProtect(app)
# app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, app.config['DATABASE_NAME'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set jinja template global
app.jinja_env.globals['momentjs'] = momentjs
login = LoginManager(app)
login.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)


from app import routes, models, utils


