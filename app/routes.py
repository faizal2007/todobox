from flask import render_template, request, redirect, url_for, make_response, jsonify, abort
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
    today_record = Todo.query.filter(Todo.status == 0, Todo.modified.ilike(
                        today.strftime("%Y-%m-%d") + '%')
                        ).order_by(Todo.modified.desc()).all()
    
    # print(datetime.now)
    # print(date.today() - timedelta(days=1))
    
    return render_template('todo.html', today_record=today_record)

@app.route('/<path:todo>/view')
def view(todo):
    if todo == 'pending':
        records = Todo.query.filter(Todo.status == 0).order_by(Todo.modified.desc()).all()
    elif todo == 'done':
        records = Todo.query.filter(Todo.status == 1).order_by(Todo.modified.desc()).all()
    else:
        abort(404)

    return render_template('view.html', records=records)

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
        getTitle = request.form.get("title").strip() 
        getActivities = request.form.get("activities").strip()
        tomorrow = datetime.now() + timedelta(days=1)
        
        if 'tomorrow' in request.form:
            getTomorrow = request.form.get("tomorrow").strip()
        else:
            getTomorrow = 0

        if request.form.get("todo_id") == '':
            if getTomorrow == 0:
                t = Todo(name=getTitle, details=getActivities)
            else:
                t = Todo(name=getTitle, details=getActivities, timestamp=None, modified=tomorrow)

            db.session.add(t)
            db.session.commit()
        else:
            id = (request.form.get("todo_id"))
            t = Todo.query.filter_by(id=id).first()
            title = t.name
            activites = t.details

            if getTitle == title and getActivities == activites :
                return make_response(
                    jsonify({
                        'status': 'failed',
                        'button':' <button type="button" class="btn btn-primary" id="save"> Save </button>'
                    })
                )
            else:
                t.name = getTitle
                t.details = getActivities
                t.modified = datetime.now()

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
    