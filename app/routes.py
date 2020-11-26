from flask import render_template, request, redirect, url_for, make_response, jsonify
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
                        ).order_by(Todo.timestamp.desc()).all()
    
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
        if request.form.get("todo_id") == '':
            t = Todo(name=request.form.get("title"), details=request.form.get("activities"))
            db.session.add(t)
            db.session.commit()
        else:
            id = (request.form.get("todo_id"))
            t = Todo.query.filter_by(id=id).first()
            title = t.name
            activites = t.details
            print(title)
            print(activites)

            if request.form.get("title") == title and request.form.get("activities") == activites :
                return make_response(
                    jsonify({
                        'status': 'failed',
                        'button':' <button type="button" class="btn btn-primary" id="save"> Save </button>'
                    })
                )
            else:
                t.name = request.form.get("title")
                t.details = request.form.get("activities")
                db.session.commit()
                return make_response(
                    jsonify({
                        'status': 'success'
                    })
                )

    return redirect(url_for('todo'))

@app.route('/<path:id>/todo', methods=['POST'])
def getTodo(id):
    
    t = Todo.query.filter_by(id=id).first()
    
    return make_response(
        jsonify({
            'status': 'Success',
            'id': t.id,
            'title': t.name,
            'activities': t.details,
            'todo-status': t.status,
            'button':' <button type="button" class="btn btn-primary" id="save"> Save </button>'
        }), 200
    )
    