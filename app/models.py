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
    email = db.Column(db.String(120), index=True, unique=True, nullable=True) # type: ignore[attr-defined]  # NULL emails allowed for system admins (NULL values are distinct in SQLite)
    fullname = db.Column(db.String(100)) # type: ignore[attr-defined]
    password_hash = db.Column(db.String(255)) # type: ignore[attr-defined]
    api_token = db.Column(db.String(255), unique=True, index=True) # type: ignore[attr-defined]  # API token for external access
    oauth_provider = db.Column(db.String(50)) # type: ignore[attr-defined]  # 'google' or None for password auth
    oauth_id = db.Column(db.String(255), index=True) # type: ignore[attr-defined]  # Google subject ID
    sharing_enabled = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Enable todo sharing (Gmail users only)
    is_admin = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Admin flag
    is_blocked = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Blocked user flag
    todo = db.relationship('Todo', backref='user', lazy='dynamic') # type: ignore[attr-defined]

    def __init__(self, username, email=None, oauth_provider=None, oauth_id=None):
        self.username = username
        self.email = email
        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id
        self.sharing_enabled = False
        # Users without email are considered system admin
        self.is_admin = (email is None or email == '')
        self.is_blocked = False

    @classmethod
    def seed(cls):
        # Admin user without email is considered system admin
        u = User(username='admin', email=None)
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
    
    def is_gmail_user(self):
        """Check if the user is a Gmail (OAuth) user"""
        return self.oauth_provider == 'google'
    
    def is_direct_login_user(self):
        """Check if the user is a direct login user (username/password authentication)"""
        return not self.oauth_provider
    
    def can_share_todos(self):
        """Check if the user can share todos (any user with sharing enabled)"""
        return self.sharing_enabled
    
    def is_system_admin(self):
        """Check if the user is a system admin.
        
        Returns True if:
        - User has is_admin flag set to True, OR
        - User has no email (users without email are always considered system admins)
        """
        return self.is_admin or (self.email is None or self.email == '')


class ShareInvitation(db.Model): # type: ignore[attr-defined]
    """Model to store pending sharing invitations between Gmail users"""
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # type: ignore[attr-defined]
    to_email = db.Column(db.String(120), nullable=False) # type: ignore[attr-defined]  # Email of user to share with
    token = db.Column(db.String(64), unique=True, index=True, nullable=False) # type: ignore[attr-defined]  # Unique token for approval link
    status = db.Column(db.String(20), default='pending') # type: ignore[attr-defined]  # pending, accepted, declined, expired
    created_at = db.Column(db.DateTime, default=datetime.now) # type: ignore[attr-defined]
    expires_at = db.Column(db.DateTime) # type: ignore[attr-defined]
    responded_at = db.Column(db.DateTime) # type: ignore[attr-defined]
    
    # Relationship to the sender
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_invitations') # type: ignore[attr-defined]
    
    def __init__(self, from_user_id, to_email, token=None, expires_in_days=7):
        import secrets
        self.from_user_id = from_user_id
        self.to_email = to_email
        self.token = token or secrets.token_urlsafe(32)
        self.status = 'pending'
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(days=expires_in_days)
    
    def is_expired(self):
        """Check if the invitation has expired"""
        return datetime.now() > self.expires_at
    
    def is_pending(self):
        """Check if the invitation is still pending"""
        return self.status == 'pending' and not self.is_expired()
    
    @property
    def display_status(self):
        """Get the display status for the invitation (handles expired pending invitations)"""
        if self.status == 'pending' and self.is_expired():
            return 'expired'
        return self.status
    
    @classmethod
    def get_by_token(cls, token):
        """Get invitation by token"""
        return cls.query.filter_by(token=token).first()


class TodoShare(db.Model): # type: ignore[attr-defined]
    """Model to track todo sharing relationships between Gmail users"""
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # type: ignore[attr-defined]  # User who owns the todos
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # type: ignore[attr-defined]  # User who can see the todos
    created_at = db.Column(db.DateTime, default=datetime.now) # type: ignore[attr-defined]
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='shared_by_me') # type: ignore[attr-defined]
    shared_with = db.relationship('User', foreign_keys=[shared_with_id], backref='shared_with_me') # type: ignore[attr-defined]
    
    # Unique constraint - each pair of users can only have one sharing relationship
    __table_args__ = (db.UniqueConstraint('owner_id', 'shared_with_id', name='unique_share'),) # type: ignore[attr-defined]
    
    def __init__(self, owner_id, shared_with_id):
        self.owner_id = owner_id
        self.shared_with_id = shared_with_id
        self.created_at = datetime.now()
    
    @classmethod
    def get_shared_users(cls, user_id):
        """Get list of users who have shared their todos with this user"""
        shares = cls.query.filter_by(shared_with_id=user_id).all()
        return [share.owner for share in shares]
    
    @classmethod
    def get_users_i_share_with(cls, user_id):
        """Get list of users this user shares their todos with"""
        shares = cls.query.filter_by(owner_id=user_id).all()
        return [share.shared_with for share in shares]
    
    @classmethod
    def is_sharing_with(cls, owner_id, shared_with_id):
        """Check if owner is sharing with the specified user"""
        return cls.query.filter_by(owner_id=owner_id, shared_with_id=shared_with_id).first() is not None


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
    # Encrypted fields - use Text to accommodate encrypted data (larger than plaintext)
    _name = db.Column('name', db.Text, index=False, nullable=False) # type: ignore[attr-defined]
    _details = db.Column('details', db.Text) # type: ignore[attr-defined]
    _details_html = db.Column('details_html', db.Text) # type: ignore[attr-defined]
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    modified = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    target_date = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # type: ignore[attr-defined]
    tracker_entries = db.relationship('Tracker', backref='todo', lazy='dynamic') # type: ignore[attr-defined]

    @property
    def name(self):
        """Decrypt and return the todo name."""
        from app.encryption import decrypt_text
        return decrypt_text(self._name)
    
    @name.setter
    def name(self, value):
        """Encrypt and store the todo name."""
        from app.encryption import encrypt_text
        self._name = encrypt_text(value)
    
    @property
    def details(self):
        """Decrypt and return the todo details."""
        from app.encryption import decrypt_text
        return decrypt_text(self._details)
    
    @details.setter
    def details(self, value):
        """Encrypt and store the todo details."""
        from app.encryption import encrypt_text
        self._details = encrypt_text(value)
    
    @property
    def details_html(self):
        """Decrypt and return the todo details HTML."""
        from app.encryption import decrypt_text
        return decrypt_text(self._details_html)
    
    @details_html.setter
    def details_html(self, value):
        """Encrypt and store the todo details HTML."""
        from app.encryption import encrypt_text
        self._details_html = encrypt_text(value)

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
