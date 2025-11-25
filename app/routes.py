from importlib.resources import path
from os import pipe
from unittest.mock import patch
from flask import render_template, request, redirect, url_for, make_response, jsonify, abort, flash, redirect
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Todo, User, Status, Tracker
from app.forms import LoginForm, ChangePassword, UpdateAccount
from urllib.parse import urlparse as url_parse
from datetime import datetime, date, timedelta
from sqlalchemy import asc
import markdown
from bleach import clean
from wtforms.csrf.core import CSRF

# Allowed HTML tags for sanitized Markdown output
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'code', 'pre', 'blockquote', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# CSRF Error Handler
@app.errorhandler(400)
def handle_csrf_error(e):
    """Handle CSRF token errors - redirect to login with session expired message"""
    if 'CSRF' in str(e) or 'csrf' in str(e).lower():
        flash('Session expired. Please login again.', 'warning')
        return redirect(url_for('login'))
    return redirect(url_for('index'))

# CSRF Validation Error Handler
@app.errorhandler(400)
def csrf_validation_error(e):
    """Handle CSRF validation errors gracefully"""
    flash('Session expired. Please login again.', 'warning')
    return redirect(url_for('login'))

"""
" Initiatiate default data
"""
@app.before_request
def initiate_data():
    if not len(User.query.all()):
        User.seed()

    if not len(Status.query.all()):
        Status.seed()

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('list', id='today'))

@app.route('/todo')
@login_required
def todo():
    #
    # Query record for today
    query_date = date.today()
    start = '{} {}'.format(query_date, '00:00')
    end = '{} {}'.format(query_date, '23:59')
    
    today_record = Todo.getList('today', start, end).order_by(Todo.timestamp.desc())
    
    return render_template('todo.html', title="Todo", today_record=today_record)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('list', id='today'))
    form = LoginForm()
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('list', id='today')
            return redirect(next_page)
    except Exception as e:
        if 'csrf' in str(e).lower():
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        raise
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    form = ChangePassword()
    try:
        if form.validate_on_submit():
            # Verify old password matches
            user = User.query.filter_by(id=current_user.id).first()
            if not user.check_password(form.oldPassword.data):
                flash('Old password is incorrect.', 'error')
            else:
                # Change password
                user.set_password(form.password.data)
                db.session.commit()  # type: ignore[attr-defined]
                flash('Password Successfully changed.', 'success')
                return redirect(url_for('security'))
    except Exception as e:
        if 'csrf' in str(e).lower():
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        raise

    return render_template('security.html', title='User Security', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(id=current_user.id).first()
            updates = []
            
            # Check and update username
            if not user.check_username(form.username.data):
                user.username = form.username.data
                updates.append('Username')
            
            # Check and update email
            if not user.check_email(form.email.data):
                user.email = form.email.data
                updates.append('Email')
            
            # Update fullname if provided
            if form.fullname.data and form.fullname.data.strip():
                user.fullname = form.fullname.data.strip()
                updates.append('Full Name')
            
            if updates:
                db.session.commit()  # type: ignore[attr-defined]
                flash(f'{", ".join(updates)} successfully updated.', 'success')
            else:
                flash('No changes made.', 'info')
    except Exception as e:
        if 'csrf' in str(e).lower():
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        raise
    
    return render_template('account.html', title='User Account', form=form)

@app.route('/<path:todo>/view')
@login_required
def view(todo):

    done = {False: "Pending", True: "Done"}

    if todo == 'pending':
        records = Todo.query.filter(Todo.status_id != 1).order_by(Todo.modified.desc()).all()
    elif todo == 'done':
        records = Todo.query.filter(Todo.status_id == 2).order_by(Todo.modified.desc()).all()
    else:
        abort(404)

    return render_template('view.html', title="Pending", records=records, done=done)

@app.route('/<path:todo_id>/delete', methods=['POST'])
@login_required
def delete(todo_id):

    Tracker.delete(todo_id)

    return redirect(url_for('todo'))

@app.route('/add', methods=['POST'])
@login_required
def add():
    if request.method == "POST":
        getTitle = (request.form.get("title") or "").strip()
        getActivities = (request.form.get("activities") or "").strip()
        getActivities_html = clean(markdown.markdown(getActivities, extensions=['fenced_code']), 
                                   tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        
        # Handle new schedule_day parameter
        schedule_day = request.form.get("schedule_day", "today")
        custom_date = request.form.get("custom_date", "")
        
        print(f"DEBUG: schedule_day={schedule_day}, custom_date={custom_date}")  # Debug line
        
        # Calculate target date based on schedule selection
        if schedule_day == "tomorrow":
            target_date = datetime.now() + timedelta(days=1)
        elif schedule_day == "custom" and custom_date:
            try:
                # Parse the date and set time to current time
                parsed_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
                current_time = datetime.now().time()
                target_date = datetime.combine(parsed_date, current_time)
                print(f"DEBUG: Parsed custom date: {target_date}")  # Debug line
            except ValueError:
                print(f"DEBUG: Invalid date format: {custom_date}")  # Debug line
                target_date = datetime.now()  # Default to today if invalid date
        else:
            target_date = datetime.now()  # Default to today
        
        tomorrow = datetime.now() + timedelta(days=1)

        if getTitle == '':
            return make_response(
                        jsonify({
                            'status': 'failed',
                            'msg': 'Title Required.'
                        })
                    )

        # Legacy support for old 'tomorrow' parameter
        if 'tomorrow' in request.form:
            getTomorrow = (request.form.get("tomorrow") or "").strip()
        else:
            getTomorrow = 0

        if request.form.get("todo_id") == '':
            # Creating new todo
            t = Todo(name=getTitle, details=getActivities, user_id=current_user.id, details_html=getActivities_html)
            
            # Override default timestamps if custom schedule is selected
            if schedule_day != "today" or getTomorrow != 0:
                # We need to set these after adding to session but before commit
                db.session.add(t)  # type: ignore[attr-defined]
                db.session.flush()  # type: ignore[attr-defined]  # This assigns the ID without committing
                
                # Now update the timestamps
                t.timestamp = target_date
                t.modified = target_date
                print(f"DEBUG: Setting custom timestamp: {target_date}")  # Debug line
            else:
                db.session.add(t)  # type: ignore[attr-defined]

            db.session.commit()  # type: ignore[attr-defined]
            
            print(f"DEBUG: Todo created with ID: {t.id}, timestamp: {t.timestamp}, modified: {t.modified}")  # Debug line
            
            # Add tracker entry with appropriate date
            if schedule_day == "today" and getTomorrow == 0:
                # For today, use the actual timestamp from the todo
                Tracker.add(t.id, 1, t.timestamp)
                print(f"DEBUG: Tracker added for TODAY with timestamp: {t.timestamp}")
            else:
                # For tomorrow or custom date, use the target_date
                Tracker.add(t.id, 1, target_date)
                print(f"DEBUG: Tracker added for {schedule_day.upper()} with timestamp: {target_date}")
        else:
            # Updating existing todo
            todo_id = request.form.get("todo_id")
            byPass = request.form.get("byPass")
            t = Todo.query.filter_by(id=todo_id).first()
            title = t.name
            activites = t.details

            if getTitle == title and getActivities == activites :
                if schedule_day != "today" or getTomorrow == '1':
                    # For tomorrow or custom date, use target_date
                    t.modified = target_date
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 4, target_date)
                    print(f"DEBUG: Updated todo (no content change) - Tracker added with timestamp: {target_date}")
                elif byPass == '1':
                    t.modified = datetime.now()
                    db.session.commit()  # type: ignore[attr-defined]
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
                t.details_html = getActivities_html
                if schedule_day != "today" or getTomorrow == '1':
                    # For tomorrow or custom date, use target_date
                    t.modified = target_date
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 4, target_date)
                    print(f"DEBUG: Updated todo (content changed) - Tracker added with timestamp: {target_date}")
                else:
                    t.modified = datetime.now()
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 1, datetime.now())
                    print(f"DEBUG: Updated todo for TODAY - Tracker added with timestamp: {datetime.now()}")
                
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
                'modified': t.modified,
                'button': button
            }), 200
        )
    return redirect(url_for('todo'))

@app.route('/<path:id>/list')
@login_required
def list(id):
    # print(Todo.getList(id))
    # abort(404)
   
    if id == 'today':
        query_date = date.today()
        start = '{} {}'.format(query_date, '00:00')
        end = '{} {}'.format(query_date, '23:59')
    elif id == 'tomorrow':
        query_date = date.today() + timedelta(days=1)
        start = '{} {}'.format(query_date, '00:00')
        end = '{} {}'.format(query_date, '23:59')
    else:
        abort(404)
        
    return render_template('list.html', title=id, todo=Todo.getList(id, start, end).order_by(asc(Tracker.timestamp)))

@app.route('/<path:id>/<path:todo_id>/done', methods=['POST'])
@login_required
def done(id, todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    date_entry = datetime.now()

    if id == 'today':
        todo.modified = date_entry
        Tracker.add(todo.id, 2, date_entry)

    return make_response(
            jsonify({
                'status': 'Success',
                'todo_id': todo.id
            }), 200
    )
