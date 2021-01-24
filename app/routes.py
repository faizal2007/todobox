from flask import render_template, request, redirect, url_for, make_response, jsonify, abort, flash, redirect
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Todo, User
from app.forms import LoginForm, ChangePassword, UpdateAccount
from werkzeug.urls import url_parse
from datetime import datetime, date, timedelta 

"""
" Initiatiate default user
"""
@app.before_first_request
def initiate_user():
    user = User.query.all()
    if len(user) == 0:
        u = User(username='admin', email='admin@examples.com')
        u.set_password('admin1234')
        db.session.add(u)
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Home")

@app.route('/todo')
@login_required
def todo():
    #
    # Query record 
    today = date.today()
    today_record = Todo.query.filter(
                                        Todo.status == False, 
                                        Todo.modified >= today.strftime("%Y-%m-%d")
                            ).order_by(
                                        Todo.modified.asc()
    ).all()
    
    return render_template('todo.html', title="Todo", today_record=today_record)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        session.permanent = True
        return redirect(url_for('todo'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_parse('todo')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    form = ChangePassword(userId=current_user.id)
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.userId.data).first()
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password Successfully changed.')
        return redirect(url_for('security'))
    
    return render_template('security.html', title='User Security', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        if user.check_username(form.username.data) and not user.check_email(form.email.data):
            """ Update Email address """
            user.email = form.email.data
            db.session.commit()
            flash('Email successfully updated.')
        elif not user.check_username(form.username.data) and user.check_email(form.email.data):
            """ Update email address """
            user.username = form.username.data
            db.session.commit()
            flash('Username updated.')
        elif not user.check_username(form.username.data) and not user.check_email(form.email.data):
            """ Update email and username address """
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash('Username updated.')
            flash('Email updated.')
        else:
            flash('No change made.')
        # print(user.check_email(form.email.data))
    return render_template('account.html', title='User Account', form=form)

@app.route('/<path:todo>/view')
@login_required
def view(todo):

    done = {False: "Pending", True: "Done"}
    
    if todo == 'pending':
        records = Todo.query.filter(Todo.status == False).order_by(Todo.modified.desc()).all()
    elif todo == 'done':
        records = Todo.query.filter(Todo.status == True).order_by(Todo.modified.desc()).all()
    else:
        abort(404)

    return render_template('view.html', title="Pending", records=records, done=done)

@app.route('/add_todo')
def add_todo():
    # t = Todo(name='Placebo bola labu', details='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante.')
    # db.session.add(t)
    # db.session.commit()
    return 'test'

@app.route('/<path:todo_id>/delete', methods=['POST'])
@login_required
def delete(todo_id):
    Todo.query.filter(Todo.id==todo_id).delete()
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/add', methods=['POST'])
@login_required
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
            id = request.form.get("todo_id")
            byPass = request.form.get("byPass")
            t = Todo.query.filter_by(id=id).first()
            title = t.name
            activites = t.details

            if getTitle == title and getActivities == activites :
                if getTomorrow == '1':
                    t.modified = datetime.now() + timedelta(days=1)
                    db.session.commit()
                elif byPass == '1':
                    t.modified = datetime.now()
                    db.session.commit()
                else:
                    return make_response(
                        jsonify({
                            'status': 'failed',
                            'button':' <button type="button" class="btn btn-primary" id="save"> Save </button>'
                        })
                    )    
            else:
                t.name = getTitle
                t.details = getActivities
                if getTomorrow == '1':
                    t.modified = datetime.now() + timedelta(days=1)
                else:
                    t.modified = datetime.now()
                
                db.session.commit()
                return make_response(
                    jsonify({
                        'status': 'success'
                    })
                )
    

    return redirect(url_for('todo'))

@app.route('/<path:id>/todo', methods=['POST'])
@login_required
def getTodo(id):
    if request.method == "POST":
        req = request.form
        t = Todo.query.filter_by(id=id).first()
        button = '<button type="button" class="btn btn-primary" id="save"> Save </button>\
                <button type="button" class="btn btn-secondary" id="tomorrow">Tomorrow</button>'

        if req.get('tbl_save') == '1':
            todoBtn = '<button type="button" class="btn btn-primary" id="todo"> Todo </button>'
            delBtn = '<button type="button" class="btn btn-warning" id="delete">Delete</button>'
            saveBtn = '<button type="button" class="btn btn-primary" id="save">Save</button>'
            if t.modified.date() == datetime.now().date():
                button = saveBtn + delBtn
            else:
                button = todoBtn + delBtn
            
        return make_response(
            jsonify({
                'status': 'Success',
                'id': t.id,
                'title': t.name,
                'activities': t.details,
                'todo-status': t.status,
                'modified': t.modified,
                'button': button
            }), 200
        )
    return redirect(url_for('todo'))
