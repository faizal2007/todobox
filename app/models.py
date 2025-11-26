from datetime import datetime, timedelta

# from sqlalchemy.orm import backref, func
from sqlalchemy import func
from sqlalchemy.sql.expression import null
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    username = db.Column(db.String(64), index=True, unique=True) # type: ignore[attr-defined]
    email = db.Column(db.String(120), index=True, unique=True) # type: ignore[attr-defined]
    fullname = db.Column(db.String(100)) # type: ignore[attr-defined]
    password_hash = db.Column(db.String(255)) # type: ignore[attr-defined]
    api_token = db.Column(db.String(255), unique=True, index=True) # type: ignore[attr-defined]  # API token for external access
    oauth_provider = db.Column(db.String(50)) # type: ignore[attr-defined]  # 'google' or None for password auth
    oauth_id = db.Column(db.String(255), index=True) # type: ignore[attr-defined]  # Google subject ID
    todo = db.relationship('Todo', backref='user', lazy='dynamic') # type: ignore[attr-defined]

    def __init__(self, username, email, oauth_provider=None, oauth_id=None):
        self.username = username
        self.email = email
        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id

    @classmethod
    def seed(cls):
        u = User(username='admin', email='admin@examples.com')
        u.set_password('admin1234')
        db.session.add(u) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_api_token(self):
        """Generate a new API token for the user"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        self.api_token = token
        db.session.commit()  # type: ignore[attr-defined]
        return token
    
    def check_api_token(self, token):
        """Check if the provided token matches the user's API token"""
        return self.api_token == token
    
    @classmethod
    def get_user_by_api_token(cls, token):
        """Get user by API token"""
        return cls.query.filter_by(api_token=token).first()
    
    def check_username(self, username):
        if self.username == username:
            return True
        else:
            return False
        
    def check_email(self, email):
        if self.email == email:
            return True
        else:
            return False

class Tracker(db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id')) # type: ignore[attr-defined]
    status_id = db.Column(db.Integer, db.ForeignKey('status.id')) # type: ignore[attr-defined]
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]

    def __init__(self, todo_id, status_id, timestamp=None):
        self.todo_id = todo_id
        self.status_id = status_id
        self.timestamp = timestamp if timestamp is not None else datetime.now()

    @classmethod
    def add(cls, todo_id, status_id, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        db.session.add(Tracker(todo_id=todo_id, status_id=status_id, timestamp=timestamp)) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]
    
    @classmethod
    def getId(cls, todo_id):
        todo = db.session.query( # type: ignore[attr-defined]
                                Tracker.id, # type: ignore[attr-defined]
                                func.max(Tracker.timestamp) # type: ignore[attr-defined]
                    ).filter(
                        Tracker.todo_id == todo_id # type: ignore[attr-defined]
                    ).group_by(Tracker.todo_id) # type: ignore[attr-defined]

        return todo.first().id

    @classmethod
    def delete(cls, todo_id):
        db.session.query(Tracker).filter(Tracker.todo_id == todo_id).delete() # type: ignore[attr-defined]
        db.session.query(Todo).filter(Todo.id == todo_id).delete() # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]

class Todo(db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    name = db.Column(db.String(80), index=True, nullable=False) # type: ignore[attr-defined]
    details = db.Column(db.String(250)) # type: ignore[attr-defined]
    details_html = db.Column(db.String(500)) # type: ignore[attr-defined]
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    modified = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    target_date = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # type: ignore[attr-defined]
    tracker_entries = db.relationship('Tracker', backref='todo', lazy='dynamic') # type: ignore[attr-defined]

    def __repr__(self):
        return '<Todo {}>'.format(self.name)

    @classmethod
    def getList(cls, type, start, end, user_id=None):
        # Validate input to prevent potential injection
        valid_types = ['today', 'tomorrow']
        if type not in valid_types:
            raise ValueError(f"Invalid type: {type}. Must be one of {valid_types}")

        done = 2
        latest_todo = db.session.query(func.max(Tracker.timestamp)).group_by(Tracker.todo_id) # type: ignore[attr-defined]
        
        query = db.session.query( # type: ignore[attr-defined]
                                Todo, 
                                Tracker
            ).join(
                    Tracker
            ).filter(
                    Tracker.timestamp == Todo.modified, # type: ignore[attr-defined]
                    Tracker.timestamp.between(start, end), # type: ignore[attr-defined]
                    Tracker.status_id != 6  # Status 6 = done # pyright: ignore[reportGeneralTypeIssues]
            )
        
        # Filter by user if user_id is provided
        if user_id is not None:
            query = query.filter(Todo.user_id == user_id) # type: ignore[attr-defined]
        
        return query

class Status(db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    name = db.Column(db.String(50), index=True, nullable=False) # type: ignore[attr-defined]
    # todo = db.relationship('Todo', backref='status', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    @classmethod
    def seed(cls):
        db.session.add(Status(id=5, name='new')) # type: ignore[attr-defined]
        db.session.add(Status(id=6, name='done')) # type: ignore[attr-defined]
        db.session.add(Status(id=7, name='failed')) # type: ignore[attr-defined]
        db.session.add(Status(id=8, name='re-assign')) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]

    def __repr__(self):
        return '<Status {}>'.format(self.name)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
