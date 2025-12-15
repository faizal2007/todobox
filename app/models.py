from datetime import datetime, timedelta

# from sqlalchemy.orm import backref, func
from sqlalchemy import func, or_
from sqlalchemy.sql.expression import null
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    email = db.Column(db.String(120), index=True, unique=True, nullable=False) # type: ignore[attr-defined]
    fullname = db.Column(db.String(100)) # type: ignore[attr-defined]
    password_hash = db.Column(db.String(255)) # type: ignore[attr-defined]
    email_verified = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Email verification status
    api_token = db.Column(db.String(255), unique=True, index=True) # type: ignore[attr-defined]  # API token for external access
    oauth_provider = db.Column(db.String(50)) # type: ignore[attr-defined]  # 'google' or None for password auth
    oauth_id = db.Column(db.String(255), index=True) # type: ignore[attr-defined]  # Google subject ID
    sharing_enabled = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Enable todo sharing (Gmail users only)
    is_admin = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Admin flag
    is_blocked = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Blocked user flag
    timezone = db.Column(db.String(50), default='UTC') # type: ignore[attr-defined]  # User's timezone (e.g., 'America/New_York')
    todo = db.relationship('Todo', backref='user', lazy='dynamic') # type: ignore[attr-defined]

    def __init__(self, email, oauth_provider=None, oauth_id=None, fullname=None):
        self.email = email
        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id
        self.fullname = fullname
        self.sharing_enabled = False
        self.timezone = 'UTC'
        # Users without email are considered system admin (though now email is required)
        self.is_admin = False
        self.is_blocked = False

    @classmethod
    def seed(cls):
        # Admin user - for now we'll use a dummy email, but this might need adjustment
        u = User(email='admin@local.local')
        u.set_password('admin1234')
        u.is_admin = True
        db.session.add(u) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]

    def __repr__(self):
        return '<User {}>'.format(self.email)
    
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

class KIV(db.Model): # type: ignore[attr-defined]
    """
    Keep In View (KIV) - separate table to manage KIV todos cleanly
    This replaces the previous status_id=9 approach
    """
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), unique=True, nullable=False) # type: ignore[attr-defined]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) # type: ignore[attr-defined]
    entered_at = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]  # When entered KIV
    exited_at = db.Column(db.DateTime, nullable=True) # type: ignore[attr-defined]  # When exited KIV (for history)
    is_active = db.Column(db.Boolean, default=True, index=True) # type: ignore[attr-defined]  # Whether currently in KIV

    def __init__(self, todo_id, user_id, entered_at=None):
        self.todo_id = todo_id
        self.user_id = user_id
        self.entered_at = entered_at if entered_at is not None else datetime.now()
        self.is_active = True

    @classmethod
    def add(cls, todo_id, user_id):
        """Add a todo to KIV"""
        kiv = cls.query.filter_by(todo_id=todo_id).first() # type: ignore[attr-defined]
        if kiv:
            # Reactivate if it was previously KIV
            kiv.is_active = True
            kiv.exited_at = None
        else:
            kiv = cls(todo_id=todo_id, user_id=user_id)
        db.session.add(kiv) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]

    @classmethod
    def remove(cls, todo_id):
        """Remove a todo from KIV (mark as exited)"""
        kiv = cls.query.filter_by(todo_id=todo_id).first() # type: ignore[attr-defined]
        if kiv:
            kiv.is_active = False
            kiv.exited_at = datetime.now()
            db.session.commit() # type: ignore[attr-defined]

    @classmethod
    def is_kiv(cls, todo_id):
        """Check if a todo is currently in KIV"""
        kiv = cls.query.filter_by(todo_id=todo_id, is_active=True).first() # type: ignore[attr-defined]
        return kiv is not None

class Todo(db.Model): # type: ignore[attr-defined]
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    # Encrypted fields - use Text to accommodate encrypted data (larger than plaintext)
    _name = db.Column('name', db.Text, index=False, nullable=False) # type: ignore[attr-defined]
    _details = db.Column('details', db.Text) # type: ignore[attr-defined]
    _details_html = db.Column('details_html', db.Text) # type: ignore[attr-defined]
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    modified = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    target_date = db.Column(db.DateTime, index=True, default=datetime.now) # type: ignore[attr-defined]
    reminder_enabled = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Whether reminder is enabled
    reminder_time = db.Column(db.DateTime, nullable=True) # type: ignore[attr-defined]  # When to send reminder (can be before target_date)
    reminder_sent = db.Column(db.Boolean, default=False) # type: ignore[attr-defined]  # Whether reminder has been sent
    reminder_notification_count = db.Column(db.Integer, default=0) # type: ignore[attr-defined]  # Count of notifications sent
    reminder_first_notification_time = db.Column(db.DateTime, nullable=True) # type: ignore[attr-defined]  # Time of first notification
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
    
    def set_reminder(self, reminder_datetime):
        """Set a reminder for this todo"""
        self.reminder_enabled = True
        self.reminder_time = reminder_datetime
        self.reminder_sent = False
        self.reminder_notification_count = 0
        self.reminder_first_notification_time = None
        db.session.commit()  # type: ignore[attr-defined]
    
    def clear_reminder(self):
        """Clear/disable reminder for this todo"""
        self.reminder_enabled = False
        self.reminder_time = None
        self.reminder_sent = False
        self.reminder_notification_count = 0
        self.reminder_first_notification_time = None
        db.session.commit()  # type: ignore[attr-defined]
    
    def has_pending_reminder(self):
        """Check if todo has a pending reminder to be sent"""
        if not self.reminder_enabled or self.reminder_sent or not self.reminder_time:
            return False
        return datetime.now() >= self.reminder_time
    
    def should_auto_close_reminder(self):
        """Check if reminder should be automatically closed (3 notifications in 30 minutes)"""
        if self.reminder_notification_count >= 3 and self.reminder_first_notification_time:
            elapsed_time = datetime.now() - self.reminder_first_notification_time
            # If 3 notifications sent within 30 minutes, auto-close
            if elapsed_time.total_seconds() <= 30 * 60:  # 30 minutes = 1800 seconds
                return True
        return False

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
                    Tracker.status_id != 6,  # Status 6 = done # pyright: ignore[reportGeneralTypeIssues]
                    Tracker.status_id != 9   # Status 9 = kiv # pyright: ignore[reportGeneralTypeIssues]
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
        statuses = [
            Status(name='new'),
            Status(name='done'),
            Status(name='failed'),
            Status(name='re-assign'),
            Status(name='kiv')
        ]
        for i, status in enumerate(statuses, start=5):
            status.id = i
        db.session.add_all(statuses)
        db.session.commit() # type: ignore[attr-defined]

    def __repr__(self):
        return '<Status {}>'.format(self.name)


class DeletedAccount(db.Model): # type: ignore[attr-defined]
    """Track deleted accounts to prevent immediate re-registration"""
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    email = db.Column(db.String(120), index=True, nullable=False) # type: ignore[attr-defined]
    oauth_id = db.Column(db.String(255)) # type: ignore[attr-defined]  # Google subject ID if OAuth user
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow) # type: ignore[attr-defined]
    cooldown_until = db.Column(db.DateTime) # type: ignore[attr-defined]  # When the email can be re-used
    
    def __init__(self, email, oauth_id=None, cooldown_days=7):
        self.email = email
        self.oauth_id = oauth_id
        self.deleted_at = datetime.utcnow()
        self.cooldown_until = datetime.utcnow() + timedelta(days=cooldown_days)
    
    @classmethod
    def is_blocked(cls, email, oauth_id=None):
        """Check if an email or OAuth ID is in cooldown period"""
        now = datetime.utcnow()
        if oauth_id:
            query = cls.query.filter(
                cls.cooldown_until > now,
                or_(cls.email == email, cls.oauth_id == oauth_id)
            )
        else:
            query = cls.query.filter(
                cls.cooldown_until > now,
                cls.email == email
            )
        return query.first() is not None
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired cooldown entries (optional maintenance)"""
        now = datetime.utcnow()
        count = cls.query.filter(cls.cooldown_until <= now).count()
        cls.query.filter(cls.cooldown_until <= now).delete()
        db.session.commit() # type: ignore[attr-defined]
        return count
    
    def __repr__(self):
        return f'<DeletedAccount {self.email}>'


class TermsAndDisclaimer(db.Model): # type: ignore[attr-defined]
    """Terms of Use and Disclaimer that users must accept before registration"""
    id = db.Column(db.Integer, primary_key=True) # type: ignore[attr-defined]
    terms_of_use = db.Column(db.Text) # type: ignore[attr-defined]  # Rich HTML content for terms
    disclaimer = db.Column(db.Text) # type: ignore[attr-defined]  # Rich HTML content for disclaimer
    version = db.Column(db.String(20), default='1.0') # type: ignore[attr-defined]  # Version number (e.g., "1.0", "1.1")
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # type: ignore[attr-defined]
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # type: ignore[attr-defined]
    is_active = db.Column(db.Boolean, default=True) # type: ignore[attr-defined]  # If False, users must accept new version
    
    def __repr__(self):
        return f'<TermsAndDisclaimer v{self.version}>'
    
    @classmethod
    def get_active(cls):
        """Get the currently active terms and disclaimer"""
        return cls.query.filter_by(is_active=True).first()
    
    @classmethod
    def get_or_create_default(cls):
        """Get active terms or create default if none exist"""
        active = cls.get_active()
        if active:
            return active
        
        # Create default terms
        default_terms = TermsAndDisclaimer(
            version='1.0',
            terms_of_use='''<h4>Terms of Use</h4>
<p>Welcome to TodoBox. By accessing and using this application, you accept and agree to be bound by the terms and provision of this agreement.</p>
<p><strong>Use License:</strong> Permission is granted to temporarily download one copy of the materials (information or software) on TodoBox for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:</p>
<ul>
    <li>Modify or copy the materials</li>
    <li>Use the materials for any commercial purpose or for any public display</li>
    <li>Attempt to decompile or reverse engineer any software contained on TodoBox</li>
    <li>Transfer the materials to another person or "mirror" the materials on any other server</li>
    <li>Attempt to gain unauthorized access to any portion or feature of the services</li>
</ul>
<p><strong>Disclaimer:</strong> The materials on TodoBox are provided on an 'as is' basis. TodoBox makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.</p>
<p><strong>Limitations:</strong> In no event shall TodoBox or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on TodoBox, even if TodoBox or an authorized representative has been notified orally or in writing of the possibility of such damage.</p>''',
            disclaimer='''<h4>Disclaimer</h4>
<p><strong>No Professional Advice:</strong> TodoBox provides a task management application for personal productivity purposes only. The service is provided on an "as-is" basis without any warranties or guarantees of any kind.</p>
<p><strong>User Responsibility:</strong> Users are solely responsible for maintaining the confidentiality of their account information and passwords. TodoBox will not be responsible for any loss or damage arising from the unauthorized use of your account.</p>
<p><strong>Data Security:</strong> While we strive to maintain reasonable security measures, no system is completely secure. By using TodoBox, you acknowledge and accept the risks associated with online data storage.</p>
<p><strong>Limitation of Liability:</strong> To the fullest extent permitted by law, TodoBox shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to, damages for lost profits, revenue, data, or business interruption.</p>
<p><strong>Changes to Terms:</strong> TodoBox reserves the right to modify these terms and conditions at any time. Your continued use of the service following any changes constitutes your acceptance of the new terms.</p>''',
            is_active=True
        )
        db.session.add(default_terms) # type: ignore[attr-defined]
        db.session.commit() # type: ignore[attr-defined]
        return default_terms


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
