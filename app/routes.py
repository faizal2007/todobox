from importlib.resources import path
from os import pipe
from unittest.mock import patch
from flask import render_template, request, redirect, url_for, make_response, jsonify, abort, flash, redirect, session
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Todo, User, Status, Tracker
from app.forms import LoginForm, ChangePassword, UpdateAccount
from app.oauth import generate_google_auth_url, process_google_callback
from urllib.parse import urlparse as url_parse
from datetime import datetime, date, timedelta
from sqlalchemy import asc, desc
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
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    from app.models import Todo, Tracker, Status
    from sqlalchemy import func, desc, and_
    
    # Get latest status for each todo  
    latest_tracker_subquery = db.session.query(  # type: ignore
        Tracker.todo_id,  # type: ignore
        func.max(Tracker.timestamp).label('latest_timestamp')
    ).group_by(Tracker.todo_id).subquery()  # type: ignore
    
    # Get proper status categorization: check if todo was EVER completed, not just current status
    chart_segments = {'done': 0, 're-assign': 0, 'pending': 0}
    
    # Get all todos and analyze each one properly
    all_todos: list = db.session.query(Todo).all()  # type: ignore
    
    for todo in all_todos:
        # Get all trackers for this todo to check completion history
        todo_trackers = db.session.query(Tracker, Status.name).join(Status).filter(  # type: ignore
            Tracker.todo_id == todo.id  # type: ignore
        ).order_by(Tracker.timestamp).all()  # type: ignore
        
        # Get latest status
        latest_tracker = db.session.query(Tracker, Status.name).join(Status).filter(  # type: ignore
            Tracker.todo_id == todo.id  # type: ignore
        ).order_by(desc(Tracker.timestamp)).first()  # type: ignore
        
        if not latest_tracker:
            continue
            
        latest_status = latest_tracker[1]
        
        # Check if todo was ever completed (has 'done' status in history)
        was_ever_completed = any(status == 'done' for _, status in todo_trackers)
        
        # Count re-assignments in history
        reassignment_count = sum(1 for _, status in todo_trackers if status == 're-assign')
        
        # Categorize todo properly
        if was_ever_completed:
            # If todo was completed, it counts as "done" regardless of current status
            chart_segments['done'] += 1
        elif reassignment_count > 0:
            # If todo was never completed but has re-assignments, count as "re-assign"
            chart_segments['re-assign'] += 1
        else:
            # If todo was never completed and never re-assigned, count as "pending"
            chart_segments['pending'] += 1
    
    # Remove zero values for cleaner chart
    chart_segments = {k: v for k, v in chart_segments.items() if v > 0}
    
    # Calculate re-assignment statistics
    reassignment_stats = {
        'total_reassignments': 0,
        'completed_after_reassignments': 0,
        'avg_reassignments_before_completion': 0.0,
        'todos_with_reassignments': 0
    }
    
    # Get all todos and analyze their re-assignment patterns
    all_todos = db.session.query(Todo).all()  # type: ignore
    
    for todo in all_todos:
        # Get all trackers for this todo ordered by timestamp
        todo_trackers = db.session.query(Tracker, Status.name).join(Status).filter(  # type: ignore
            Tracker.todo_id == todo.id  # type: ignore
        ).order_by(Tracker.timestamp).all()  # type: ignore
        
        reassign_count = 0
        is_completed = False
        
        # Count re-assignments and check if completed
        for tracker, status_name in todo_trackers:
            if status_name == 're-assign':
                reassign_count += 1
            elif status_name == 'done':
                is_completed = True
        
        # Update statistics
        if reassign_count > 0:
            reassignment_stats['todos_with_reassignments'] += 1
        
        reassignment_stats['total_reassignments'] += reassign_count
        
        if is_completed:
            reassignment_stats['completed_after_reassignments'] += reassign_count
    
    # Calculate average re-assignments before completion  
    # We already have the completion data from our loop above
    completed_todos_count = chart_segments['done']
    
    if completed_todos_count > 0:
        reassignment_stats['avg_reassignments_before_completion'] = round(
            reassignment_stats['completed_after_reassignments'] / completed_todos_count, 1
        )
    else:
        reassignment_stats['avg_reassignments_before_completion'] = 0.0
    
    # Get recent todos for activity feed
    recent_todos = db.session.query(Todo).order_by(desc(Todo.timestamp)).limit(5).all()  # type: ignore
    
    return render_template('dashboard.html', 
                         chart_segments=chart_segments,
                         recent_todos=recent_todos,
                         reassignment_stats=reassignment_stats)

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

@app.route('/auth/login/google')
def oauth_login_google():
    """Redirect user to Google for authentication"""
    auth_url = generate_google_auth_url()
    return redirect(auth_url)

@app.route('/auth/callback/google')
def oauth_callback_google():
    """Handle Google OAuth callback"""
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        flash('Google authentication failed. Please try again.', 'warning')
        return redirect(url_for('login'))
    
    if not code:
        flash('Authentication failed: no authorization code received.', 'warning')
        return redirect(url_for('login'))
    
    # Process the Google callback
    user, is_new = process_google_callback(code)
    
    if not user:
        flash('Google authentication failed. Please try again or use password login.', 'warning')
        return redirect(url_for('login'))
    
    # Log in the user
    login_user(user, remember=True)
    
    if is_new:
        flash(f'Welcome! Your account has been created with {user.email}', 'success')
        next_page = url_for('account')  # Redirect to account page to complete profile
    else:
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next') or url_for('list', id='today')
    
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('list', id='today')
    
    return redirect(next_page)

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

@app.route('/undone')
@login_required
def undone():
    """Show all undone/pending todos across all dates"""
    # Get all todos that are not completed (status_id != 2)
    # Use a simpler approach - get all todos and filter by latest tracker status
    
    undone_todos = []
    all_todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.modified.desc()).all()
    
    for todo in all_todos:
        # Get the latest tracker entry for this todo
        latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(Tracker.timestamp.desc()).first()  # type: ignore[attr-defined]
        
        # Only include if the latest status is not completed (status_id != 2)
        if latest_tracker and latest_tracker.status_id != 2:
            undone_todos.append((todo, latest_tracker))
    
    return render_template('undone.html', title='Undone Tasks', todos=undone_todos)

@app.route('/<path:todo_id>/done', methods=['POST'])
@login_required
def mark_done(todo_id):
    """Mark a todo as done from any page"""
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo:
        date_entry = datetime.now()
        todo.modified = date_entry
        db.session.commit()  # type: ignore[attr-defined]
        Tracker.add(todo.id, 2, date_entry)  # Status 2 = Done

    return make_response(
        jsonify({
            'status': 'Success',
            'todo_id': todo.id if todo else None
        }), 200
    )

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

    return redirect(url_for('list', id='today'))

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


    return redirect(url_for('list', id='today'))

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
    return redirect(url_for('list', id='today'))

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
        
    return render_template('list.html', title=id, todo=Todo.getList(id, start, end).order_by(desc(Tracker.timestamp)))

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
