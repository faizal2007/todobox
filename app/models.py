from datetime import datetime
from app import db

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    details = db.Column(db.String(250))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modified = db.Column(db.DateTime, index=True, default=datetime.now)
    status = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<Todo {}'.format(self.name)