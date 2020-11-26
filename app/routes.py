from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Todo
from datetime import datetime, date, timedelta 

@app.route('/')
@app.route('/index')
def index():
    # return ''
    return render_template('index.html')

@app.route('/todo')
def todo():
    #
    # Query record 
    today = date.today()
    today_record = Todo.query.filter(Todo.status == 0, Todo.timestamp.ilike(
                        today.strftime("%Y-%m-%d") + '%')
                        ).all()
    
    
    # print(datetime.now)
    # print(date.today() - timedelta(days=1))
    
    return render_template('todo.html', today_record=today_record)

@app.route('/add_todo')
def add_todo():
    t = Todo(name='Placebo bola labu', details='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante.')
    db.session.add(t)
    db.session.commit()
    return 'test'

@app.route('/<path:todo_id>/delete', methods=['POST'])
def delete(todo_id):
    Todo.query.filter(Todo.id==todo_id).delete()
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/add', methods=['POST'])
def add():
    if request.method == "POST":
        print(request.form.get("title"))
        print(request.form.get("activities"))
        t = Todo(name=request.form.get("title"), details=request.form.get("activities"))
        db.session.add(t)
        db.session.commit()
    return redirect(url_for('todo'))
    