from flask import render_template
from app import app, db
from app.models import Todo
from datetime import datetime, date 

@app.route('/')
@app.route('/index')
def index():
    # return ''
    return render_template('index.html')

@app.route('/todo')
def todo():
    # todo_record = db.session.query(Todo).filter_by(status=0).all()
    todo_record = Todo.query.filter_by(status=0).all()
    print(date.today())
    
    return render_template('todo.html', todo_record=todo_record)

@app.route('/add_todo')
def add_todo():
    t = Todo(name='Study Gimp', details='Add just image')
    db.session.add(t)
    db.session.commit()
    return 'test'
    