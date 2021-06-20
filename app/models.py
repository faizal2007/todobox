from datetime import datetime, timedelta

# from sqlalchemy.orm import backref, func
from sqlalchemy import func
from sqlalchemy.sql.expression import null
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    fullname = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))
    todo = db.relationship('Todo', backref='user', lazy='dynamic')

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def seed():
        u = User(username='admin', email='admin@examples.com')
        u.set_password('admin1234')
        db.session.add(u)
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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

class Tracker(object):
    def __init__(self, todo_id, status_id, timestamp):
        self.todo_id = todo_id
        self.status_id =  status_id
        self.timestamp = timestamp

    def add(todo_id, status_id, timestamp=datetime.now()):
        print(timestamp)
        db.session.add(Tracker(todo_id=todo_id, status_id=status_id, timestamp=timestamp))
        db.session.commit()
    
    def getId(todo_id):
        todo = db.session.query( 
                                Tracker.id,
                                func.max(Tracker.timestamp)
                    ).filter(
                        Tracker.todo_id == todo_id
                    ).group_by(Tracker.todo_id)

        return todo.first().id

tracker = db.Table('tracker',
        db.metadata,
        db.Column('id', db.Integer, primary_key=True),
        db.Column('todo_id', db.Integer, db.ForeignKey('todo.id')),
        db.Column('status_id', db.Integer, db.ForeignKey('status.id')),
        db.Column('timestamp', db.DateTime, index=True, default=datetime.now)
)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, nullable=False)
    details = db.Column(db.String(250))
    details_html = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modified = db.Column(db.DateTime, index=True, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tracker = db.relationship('Status', secondary=tracker, backref=db.backref('todo', lazy='dynamic'))

    def __repr__(self):
        return '<Todo {}'.format(self.name)

    def getList(type, start, end):

        done = 2
        latest_todo = db.session.query(func.max(Tracker.timestamp)).group_by(Tracker.todo_id)
        
        todo = db.session.query(
                                Todo, 
                                Tracker
            ).join(
                    Tracker
            ).filter(
                    Tracker.timestamp.in_(latest_todo),
                    Tracker.timestamp.between(start, end),
                    Tracker.status_id != done
            )
        return todo

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    # todo = db.relationship('Todo', backref='status', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def seed():
        db.session.add(Status(name = 'new'))
        db.session.add(Status(name = 'done'))
        db.session.add(Status(name = 'failed'))
        db.session.add(Status(name = 're-assign'))
        db.session.commit()

    def __repr__(self):
        return '<Todo {}'.format(self.name)

db.mapper(Tracker, tracker)
db.create_all()

    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
