from importlib.resources import path
from os import pipe
from unittest.mock import patch
from flask import render_template, request, redirect, url_for, make_response, jsonify, abort, flash, redirect, session, g
from app import app, db, csrf
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Todo, User, Status, Tracker, ShareInvitation, TodoShare
from app.forms import LoginForm, SetupAccountForm, ChangePassword, UpdateAccount, ShareInvitationForm, SharingSettingsForm
from app.oauth import generate_google_auth_url, process_google_callback, OAuthError
from app.email_service import send_sharing_invitation, get_invitation_link, is_email_configured
from urllib.parse import urlparse as url_parse
from datetime import datetime, date, timedelta
from sqlalchemy import asc, desc, or_
import markdown
from bleach import clean
from wtforms.csrf.core import CSRF
from functools import wraps
import requests

# API Token Authentication Decorator
def require_api_token(f):
    """Decorator to require API token authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid API token'}), 401
        
        token = auth_header.split(' ')[1]
        user = User.get_user_by_api_token(token)
        if not user:
            return jsonify({'error': 'Invalid API token'}), 401
        
        # Add user to Flask g object for the request context
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

# Allowed HTML tags for sanitized Markdown output
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'code', 'pre', 'blockquote', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# CSRF Error Handler - only for web routes
@app.errorhandler(400)
def handle_csrf_error(e):
    """Handle CSRF token errors - redirect to login with session expired message"""
    if 'CSRF' in str(e) or 'csrf' in str(e).lower():
        # Check if this is an API request
        if request.path.startswith('/api/'):
            return jsonify({'error': 'CSRF validation failed'}), 400
        flash('Session expired. Please login again.', 'warning')
        return redirect(url_for('login'))
    return redirect(url_for('index'))

# CSRF Validation Error Handler
@app.errorhandler(400)
def csrf_validation_error(e):
    """Handle CSRF validation errors gracefully"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'CSRF validation failed'}), 400
    flash('Session expired. Please login again.', 'warning')
    return redirect(url_for('login'))

# Fallback local quotes
LOCAL_QUOTES = [
    "Stay focused",
    "Keep it simple",
    "Progress over perfection",
    "One step at a time",
    "You got this",
    "Be present",
    "Make it count",
    "Dream big",
    "Start now",
    "Stay curious",
    "Do better",
    "Be kind",
    "Never stop learning",
    "Create value",
    "Think different"
]

@app.route('/api/quote')
@csrf.exempt
def get_quote():
    """Return a local quote without external API calls"""
    import random
    fallback_quote = random.choice(LOCAL_QUOTES)
    return jsonify({'quote': fallback_quote})

@app.route('/api/auth/token', methods=['POST'])
@csrf.exempt
@login_required
def generate_api_token():
    """Generate a new API token for the authenticated user"""
    token = current_user.generate_api_token()
    return jsonify({
        'token': token,
        'message': 'API token generated successfully. Keep this token secure!'
    })

@app.route('/api/todo', methods=['GET'])
@csrf.exempt
@require_api_token
def get_todos():
    """Get all todos for the authenticated user"""
    user = g.user
    
    # Get all todos for the user
    todos = Todo.query.filter_by(user_id=user.id).all()
    
    todo_list = []
    for todo in todos:
        # Get latest status
        latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(desc(Tracker.timestamp)).first()
        status = 'pending'
        if latest_tracker:
            status_obj = Status.query.get(latest_tracker.status_id)
            if status_obj:
                status = status_obj.name
        
        todo_list.append({
            'id': todo.id,
            'title': todo.name,
            'details': todo.details,
            'status': status,
            'created_at': todo.timestamp.isoformat(),
            'modified_at': todo.modified.isoformat()
        })
    
    return jsonify({'todos': todo_list})

@app.route('/api/todo', methods=['POST'])
@csrf.exempt
@require_api_token
def create_todo():
    """Create a new todo for the authenticated user"""
    user = g.user

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    title = data['title'].strip()
    details = data.get('details', '').strip()
    
    if not title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    # Create todo
    details_html = clean(markdown.markdown(details, extensions=['fenced_code']), 
                        tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    todo = Todo(name=title, details=details, details_html=details_html, user_id=user.id)
    db.session.add(todo)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    # Add tracker entry
    Tracker.add(todo.id, 5, todo.timestamp)  # Status 5 = new
    
    return jsonify({
        'id': todo.id,
        'title': todo.name,
        'details': todo.details,
        'status': 'pending',
        'created_at': todo.timestamp.isoformat(),
        'modified_at': todo.modified.isoformat()
    }), 201

@app.route('/api/todo/<int:todo_id>', methods=['PUT'])
@csrf.exempt
@require_api_token
def update_todo(todo_id):
    """Update a todo for the authenticated user"""
    user = g.user
    
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        todo.name = title
    
    if 'details' in data:
        details = data['details'].strip()
        todo.details = details
        todo.details_html = clean(markdown.markdown(details, extensions=['fenced_code']), 
                                 tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    if 'status' in data:
        status_name = data['status']
        status = Status.query.filter_by(name=status_name).first()
        if status:
            todo.modified = datetime.now()
            Tracker.add(todo.id, status.id, todo.modified)
    
    db.session.commit()  # type: ignore[attr-defined]
    
    # Get current status
    latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(desc(Tracker.timestamp)).first()
    current_status = 'pending'
    if latest_tracker:
        status_obj = Status.query.get(latest_tracker.status_id)
        if status_obj:
            current_status = status_obj.name
    
    return jsonify({
        'id': todo.id,
        'title': todo.name,
        'details': todo.details,
        'status': current_status,
        'created_at': todo.timestamp.isoformat(),
        'modified_at': todo.modified.isoformat()
    })

@app.route('/api/todo/<int:todo_id>', methods=['DELETE'])
@csrf.exempt
@require_api_token
def delete_todo(todo_id):
    """Delete a todo for the authenticated user"""
    user = g.user
    
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Delete trackers first
    Tracker.query.filter_by(todo_id=todo_id).delete()
    # Delete todo
    db.session.delete(todo)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    return jsonify({'message': 'Todo deleted successfully'})

"""
" Initiatiate default data
"""
"""
" Initialize default data on app startup
"""
def init_default_data():
    """Initialize default data on application startup"""
    try:
        with app.app_context():
            # Check and seed users if none exist
            user_count = User.query.count()
            if user_count == 0:
                User.seed()

            # Always check and seed status records - be more robust
            status_count = Status.query.count()
            if status_count == 0:
                Status.seed()
                db.session.commit()  # type: ignore[attr-defined]
    except Exception as e:
        print(f"ERROR: Failed to initialize default data: {e}")
        # Don't let this crash the app, but log the error
        import traceback
        traceback.print_exc()

# Initialize data once when app starts
# init_default_data()  # DISABLED - moved to app startup hook

@app.route('/')
def root():
    """Root route - redirect to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

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
    completed_todos_count = chart_segments.get('done', 0)
    
    if completed_todos_count > 0:
        reassignment_stats['avg_reassignments_before_completion'] = round(
            reassignment_stats['completed_after_reassignments'] / completed_todos_count, 1
        )
    else:
        reassignment_stats['avg_reassignments_before_completion'] = 0.0
    
    # Get recent undone todos for activity feed (filtered by current user and not completed)
    # Using a similar pattern to getList() in models.py - matching tracker timestamp to todo modified time
    # Status 6 = 'done' (see Status.seed() in models.py)
    recent_todos = db.session.query(Todo).join(
        Tracker, Todo.id == Tracker.todo_id
    ).filter(
        Todo.user_id == current_user.id,
        Tracker.timestamp == Todo.modified,  # Match the latest tracker (same pattern as getList)
        Tracker.status_id != 6  # Status 6 = 'done'
    ).order_by(Todo.modified.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         chart_segments=chart_segments,
                         recent_todos=recent_todos,
                         reassignment_stats=reassignment_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if any users exist - if not, redirect to setup
    try:
        user_count = User.query.count()
        if user_count == 0:
            return redirect(url_for('setup'))
    except Exception:
        # If database is not accessible, assume no users and redirect to setup
        return redirect(url_for('setup'))
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid email or password')
                return redirect(url_for('login'))
            # Check if user is blocked
            if user.is_blocked:
                flash('Your account has been blocked. Please contact an administrator.', 'error')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
    except Exception as e:
        if 'csrf' in str(e).lower():
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        raise
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/setup')
def setup():
    """Setup page for first-time users"""
    # Only show setup if no users exist
    try:
        user_count = User.query.count()
        if user_count > 0:
            return redirect(url_for('login'))
    except Exception:
        # If database is not accessible, still show setup
        pass
    
    return render_template('setup.html', title='Setup TodoBox')

@app.route('/setup/account', methods=['GET', 'POST'])
def setup_account():
    """Create first user account"""
    # Check database connection first
    db_error = None
    try:
        user_count = User.query.count()
        if user_count > 0:
            return redirect(url_for('login'))
    except Exception as e:
        db_error = str(e)
        # Check if it's a connection error
        if 'password authentication failed' in db_error or 'connection to server' in db_error:
            db_error = "Database connection failed. Please check your database configuration."
        elif 'connect' in db_error.lower():
            db_error = "Cannot connect to database. Please verify your database is running and credentials are correct."
        else:
            db_error = "Database error occurred. Please check your database setup."
    
    form = SetupAccountForm()
    
    try:
        if form.validate_on_submit():
            # Check database connection again before creating user
            if db_error:
                flash('Database connection error: ' + db_error, 'danger')
                return render_template('setup_account.html', title='Create Account', form=form, db_error=db_error)
            
            # Create the user
            user = User(
                email=form.email.data
            )
            user.set_password(form.password.data)
            if form.fullname.data and form.fullname.data.strip():
                user.fullname = form.fullname.data.strip()
            
            db.session.add(user)  # type: ignore[attr-defined]
            db.session.commit()  # type: ignore[attr-defined]
            
            # Log in the user
            login_user(user, remember=True)
            
            flash('Welcome to TodoBox! Your account has been created successfully.', 'success')
            return redirect(url_for('dashboard'))
    except Exception as e:
        error_msg = str(e)
        if 'password authentication failed' in error_msg or 'connection to server' in error_msg:
            db_error = "Database connection failed. Please check your database configuration."
            flash('Database connection error: ' + db_error, 'danger')
        elif 'connect' in error_msg.lower():
            db_error = "Cannot connect to database. Please verify your database is running and credentials are correct."
            flash('Database connection error: ' + db_error, 'danger')
        elif 'csrf' in error_msg.lower():
            flash('Session expired. Please try again.', 'warning')
            return redirect(url_for('setup_account'))
        else:
            flash('An error occurred while creating your account. Please try again.', 'danger')
            app.logger.error(f"Account creation error: {error_msg}")
    
    return render_template('setup_account.html', title='Create Account', form=form, db_error=db_error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/auth/login/google')
def oauth_login_google():
    """Redirect user to Google for authentication"""
    try:
        auth_url = generate_google_auth_url()
        return redirect(auth_url)
    except OAuthError as e:
        app.logger.error(f"OAuth error: {str(e)}")
        flash('Unable to connect to Google authentication service. Please try again later or use password login.', 'warning')
        return redirect(url_for('login'))

@app.route('/auth/callback/google')
def oauth_callback_google():
    """Handle Google OAuth callback"""
    code = request.args.get("code")
    returned_state = request.args.get("state")
    error = request.args.get("error")
    
    if error:
        flash('Google authentication failed. Please try again.', 'warning')
        return redirect(url_for('login'))
    
    # Validate state to protect against CSRF
    expected_state = session.pop('oauth_state', None)
    if expected_state and returned_state != expected_state:
        flash('Authentication failed: invalid session state.', 'warning')
        return redirect(url_for('login'))

    if not code:
        flash('Authentication failed: no authorization code received.', 'warning')
        return redirect(url_for('login'))
    
    # Process the Google callback
    user, is_new = process_google_callback(code)
    
    if not user:
        flash('Google authentication failed. Please try again or use password login.', 'warning')
        return redirect(url_for('login'))
    
    # Check if user is blocked
    if user.is_blocked:
        flash('Your account has been blocked. Please contact an administrator.', 'error')
        return redirect(url_for('login'))
    
    # Log in the user
    login_user(user, remember=True)
    
    if is_new:
        flash(f'Welcome! Your account has been created with {user.email}', 'success')
        next_page = url_for('account')  # Redirect to account page to complete profile
    else:
        display_name = user.fullname or user.email
        flash(f'Welcome back, {display_name}!', 'success')
        next_page = request.args.get('next') or url_for('dashboard')
    
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('dashboard')
    
    return redirect(next_page)


@app.route('/diag/oauth')
@login_required
@require_admin
def diag_oauth():
    """Diagnostic endpoint for OAuth/Proxy setup (admin only)."""
    try:
        generated = url_for("oauth_callback_google", _external=True)
    except Exception:
        generated = None

    info = {
        "configured_redirect_uri": app.config.get("OAUTH_REDIRECT_URI"),
        "generated_redirect_uri": generated,
        "preferred_url_scheme": app.config.get("PREFERRED_URL_SCHEME"),
        "proxy_trust": {
            "x_for": app.config.get('PROXY_X_FOR'),
            "x_proto": app.config.get('PROXY_X_PROTO'),
            "x_host": app.config.get('PROXY_X_HOST'),
            "x_prefix": app.config.get('PROXY_X_PREFIX')
        },
        "google_prompt": app.config.get("GOOGLE_OAUTH_PROMPT"),
        "headers": {
            "X-Forwarded-Host": request.headers.get('X-Forwarded-Host'),
            "X-Forwarded-Proto": request.headers.get('X-Forwarded-Proto'),
            "Host": request.headers.get('Host')
        }
    }
    return jsonify(info)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(id=current_user.id).first()
            updates = []
            
            # Username changes are disabled
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
        
        # Only include if the latest status is not completed (status_id != 6)
        if latest_tracker and latest_tracker.status_id != 6:
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
        Tracker.add(todo.id, 6, date_entry)  # Status 6 = Done

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
        # Get todos where the latest tracker status is not 'new' (status_id != 5)
        records = []
        all_todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.modified.desc()).all()
        for t in all_todos:
            latest_tracker = Tracker.query.filter_by(todo_id=t.id).order_by(Tracker.timestamp.desc()).first() # pyright: ignore[reportAttributeAccessIssue]
            if latest_tracker and latest_tracker.status_id != 5:  # Not new
                records.append(t)
    elif todo == 'done':
        # Get todos where the latest tracker status is 'done' (status_id == 6)
        records = []
        all_todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.modified.desc()).all()
        for t in all_todos:
            latest_tracker = Tracker.query.filter_by(todo_id=t.id).order_by(Tracker.timestamp.desc()).first() # pyright: ignore[reportAttributeAccessIssue]
            if latest_tracker and latest_tracker.status_id == 6:  # Done
                records.append(t)
    else:
        abort(404)

    return render_template('view.html', title="Pending", records=records, done=done)

@app.route('/<path:todo_id>/delete', methods=['POST'])
@login_required
def delete(todo_id):
    # Verify todo belongs to current user before deleting
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        abort(404)
    
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
                Tracker.add(t.id, 5, t.timestamp)  # Status 5 = new
                print(f"DEBUG: Tracker added for TODAY with timestamp: {t.timestamp}")
            else:
                # For tomorrow or custom date, use the target_date
                Tracker.add(t.id, 5, target_date)  # Status 5 = new
                print(f"DEBUG: Tracker added for {schedule_day.upper()} with timestamp: {target_date}")
        else:
            # Updating existing todo
            todo_id = request.form.get("todo_id")
            byPass = request.form.get("byPass")
            # Filter by user_id to ensure user can only update their own todos
            t = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
            if not t:
                return make_response(
                    jsonify({
                        'status': 'failed',
                        'msg': 'Todo not found or access denied.'
                    })
                )
            title = t.name
            activites = t.details

            if getTitle == title and getActivities == activites :
                if schedule_day != "today" or getTomorrow == '1':
                    # For tomorrow or custom date, use target_date
                    t.modified = target_date
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 8, target_date)  # Status 8 = re-assign
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
                    Tracker.add(todo_id, 8, target_date)  # Status 8 = re-assign
                    print(f"DEBUG: Updated todo (content changed) - Tracker added with timestamp: {target_date}")
                else:
                    t.modified = datetime.now()
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 5, datetime.now())  # Status 5 = new
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
        # First try to get the todo owned by the current user
        t = Todo.query.filter_by(id=id, user_id=current_user.id).first()
        is_shared = False
        
        # If not found, check if it's a shared todo
        if not t:
            t = Todo.query.filter_by(id=id).first()
            if t:
                # Check if the todo owner has shared with the current user
                if TodoShare.is_sharing_with(t.user_id, current_user.id):
                    is_shared = True
                else:
                    t = None  # Reset - user doesn't have access
        
        if not t:
            return make_response(
                jsonify({
                    'status': 'Error',
                    'message': 'Todo not found'
                }), 404
            )
        
        # For shared todos, show read-only view (no edit/delete buttons)
        if is_shared:
            button = ''  # No action buttons for shared todos
        else:
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
        
    return render_template('list.html', title=id, todo=Todo.getList(id, start, end, user_id=current_user.id).order_by(desc(Tracker.timestamp)))

@app.route('/<path:id>/<path:todo_id>/done', methods=['POST'])
@login_required
def done(id, todo_id):
    # Filter by user_id to ensure user can only mark their own todos as done
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return make_response(
            jsonify({
                'status': 'Error',
                'message': 'Todo not found'
            }), 404
        )
    date_entry = datetime.now()

    if id == 'today':
        todo.modified = date_entry
        Tracker.add(todo.id, 6, date_entry)  # Status 6 = Done

    return make_response(
            jsonify({
                'status': 'Success',
                'todo_id': todo.id
            }), 200
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page for managing password and API tokens"""
    password_form = ChangePassword()
    
    # Handle password change
    if password_form.validate_on_submit() and 'change_password' in request.form:
        try:
            # Verify old password matches
            user = User.query.filter_by(id=current_user.id).first()
            if not user.check_password(password_form.oldPassword.data):
                flash('Old password is incorrect.', 'error')
            else:
                # Change password
                user.set_password(password_form.password.data)
                db.session.commit()  # type: ignore[attr-defined]
                flash('Password changed successfully.', 'success')
                return redirect(url_for('settings'))
        except Exception as e:
            if 'csrf' in str(e).lower():
                flash('Session expired. Please login again.', 'warning')
                return redirect(url_for('login'))
            raise
    
    # Handle API token actions
    if request.method == 'POST':
        if 'generate_token' in request.form:
            # Generate new API token
            token = current_user.generate_api_token()
            flash('New API token generated successfully!', 'success')
            return redirect(url_for('settings'))
        elif 'revoke_token' in request.form:
            # Revoke current API token
            current_user.api_token = None
            db.session.commit()  # type: ignore[attr-defined]
            flash('API token revoked successfully!', 'success')
            return redirect(url_for('settings'))
    
    return render_template('settings.html', title='Settings', password_form=password_form)


# ==================== Todo Sharing Routes ====================

@app.route('/sharing/toggle', methods=['POST'])
@login_required
def toggle_sharing():
    """AJAX endpoint to toggle sharing enabled/disabled"""
    data = request.get_json()
    if data is None:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    sharing_enabled = data.get('sharing_enabled', False)
    current_user.sharing_enabled = sharing_enabled
    db.session.commit()  # type: ignore[attr-defined]
    
    return jsonify({
        'status': 'success',
        'message': 'Sharing settings updated successfully.',
        'sharing_enabled': current_user.sharing_enabled
    })


@app.route('/sharing', methods=['GET', 'POST'])
@login_required
def sharing():
    """Sharing settings and invitation management page"""
    settings_form = SharingSettingsForm()
    invitation_form = ShareInvitationForm()
    
    # Handle sharing settings update
    if request.method == 'POST' and 'save_settings' in request.form:
        current_user.sharing_enabled = 'sharing_enabled' in request.form
        db.session.commit()  # type: ignore[attr-defined]
        flash('Sharing settings updated successfully.', 'success')
        return redirect(url_for('sharing'))
    
    # Handle sending invitation
    if request.method == 'POST' and 'send_invitation' in request.form:
        if not current_user.sharing_enabled:
            flash('Please enable sharing first before sending invitations.', 'warning')
            return redirect(url_for('sharing'))
        
        if invitation_form.validate():
            to_email = invitation_form.email.data.lower().strip()
            
            # Check if already sharing with this user
            existing_user = User.query.filter_by(email=to_email).first()
            if existing_user and TodoShare.is_sharing_with(current_user.id, existing_user.id):
                flash(f'You are already sharing todos with {to_email}.', 'info')
                return redirect(url_for('sharing'))
            
            # Check for pending invitation
            pending = ShareInvitation.query.filter_by(
                from_user_id=current_user.id,
                to_email=to_email,
                status='pending'
            ).first()
            
            if pending and not pending.is_expired():
                flash(f'An invitation to {to_email} is already pending.', 'info')
                return redirect(url_for('sharing'))
            
            # Create new invitation
            invitation = ShareInvitation(from_user_id=current_user.id, to_email=to_email)
            db.session.add(invitation)  # type: ignore[attr-defined]
            db.session.commit()  # type: ignore[attr-defined]
            
            # Try to send email
            if is_email_configured():
                success, error = send_sharing_invitation(invitation, current_user)
                if success:
                    flash(f'Invitation sent to {to_email}!', 'success')
                else:
                    # Email failed but invitation created - show link
                    invitation_link = get_invitation_link(invitation)
                    flash(f'Could not send email ({error}). Share this link manually: {invitation_link}', 'warning')
            else:
                # Email not configured - show link
                invitation_link = get_invitation_link(invitation)
                flash(f'Email not configured. Share this link with {to_email}: {invitation_link}', 'info')
            
            return redirect(url_for('sharing'))
    
    # Get current user's sent invitations (pending ones)
    sent_invitations = ShareInvitation.query.filter_by(
        from_user_id=current_user.id
    ).order_by(ShareInvitation.created_at.desc()).limit(10).all()
    
    # Get received invitations (pending and not expired) - use database filter for efficiency
    received_invitations = ShareInvitation.query.filter(
        ShareInvitation.to_email == current_user.email,
        ShareInvitation.status == 'pending',
        ShareInvitation.expires_at > datetime.now()
    ).all()
    
    # Get current sharing relationships
    shared_with_me = TodoShare.get_shared_users(current_user.id)
    i_share_with = TodoShare.get_users_i_share_with(current_user.id)
    
    # Pre-set the checkbox value
    settings_form.sharing_enabled.data = current_user.sharing_enabled
    
    return render_template('sharing.html', 
                          title='Sharing Settings',
                          settings_form=settings_form,
                          invitation_form=invitation_form,
                          sent_invitations=sent_invitations,
                          received_invitations=received_invitations,
                          shared_with_me=shared_with_me,
                          i_share_with=i_share_with,
                          email_configured=is_email_configured())


@app.route('/share/accept/<token>')
def accept_share_invitation(token):
    """Accept a sharing invitation"""
    invitation = ShareInvitation.get_by_token(token)
    
    if not invitation:
        flash('Invalid invitation link.', 'error')
        return redirect(url_for('login'))
    
    if invitation.is_expired():
        invitation.status = 'expired'
        db.session.commit()  # type: ignore[attr-defined]
        flash('This invitation has expired.', 'warning')
        return redirect(url_for('login'))
    
    if invitation.status != 'pending':
        flash(f'This invitation has already been {invitation.status}.', 'info')
        return redirect(url_for('login'))
    
    # User must be logged in to accept
    if not current_user.is_authenticated:
        # Store invitation token in session for after login
        session['pending_share_token'] = token
        flash('Please sign in to accept this sharing invitation.', 'info')
        return redirect(url_for('login'))
    
    # Check if the logged-in user's email matches the invitation
    if current_user.email.lower() != invitation.to_email.lower():
        flash(f'This invitation was sent to {invitation.to_email}. Please sign in with that account.', 'warning')
        return redirect(url_for('login'))
    
    # Accept the invitation
    invitation.status = 'accepted'
    invitation.responded_at = datetime.now()
    
    # Create the sharing relationship with race condition handling
    from sqlalchemy.exc import IntegrityError
    try:
        existing_share = TodoShare.query.filter_by(
            owner_id=invitation.from_user_id,
            shared_with_id=current_user.id
        ).first()
        
        if not existing_share:
            share = TodoShare(owner_id=invitation.from_user_id, shared_with_id=current_user.id)
            db.session.add(share)  # type: ignore[attr-defined]
        
        db.session.commit()  # type: ignore[attr-defined]
    except IntegrityError:
        # Handle potential race condition - unique constraint violation
        db.session.rollback()  # type: ignore[attr-defined]
        # Re-check if share exists (created by concurrent request)
        existing_share = TodoShare.query.filter_by(
            owner_id=invitation.from_user_id,
            shared_with_id=current_user.id
        ).first()
        if not existing_share:
            # If share still doesn't exist, re-raise the exception
            raise
        # Update invitation status separately
        invitation.status = 'accepted'
        invitation.responded_at = datetime.now()
        db.session.commit()  # type: ignore[attr-defined]
    
    from_user = User.query.get(invitation.from_user_id)
    flash(f'You can now see todos shared by {from_user.fullname or from_user.username}!', 'success')
    return redirect(url_for('shared_todos'))


@app.route('/share/decline/<token>')
def decline_share_invitation(token):
    """Decline a sharing invitation"""
    invitation = ShareInvitation.get_by_token(token)
    
    if not invitation:
        flash('Invalid invitation link.', 'error')
        return redirect(url_for('login'))
    
    if invitation.status != 'pending':
        flash(f'This invitation has already been {invitation.status}.', 'info')
        return redirect(url_for('login'))
    
    # Decline the invitation
    invitation.status = 'declined'
    invitation.responded_at = datetime.now()
    db.session.commit()  # type: ignore[attr-defined]
    
    flash('Invitation declined.', 'info')
    if current_user.is_authenticated:
        return redirect(url_for('sharing'))
    return redirect(url_for('login'))


@app.route('/share/revoke/<int:share_id>', methods=['POST'])
@login_required
def revoke_share(share_id):
    """Revoke a sharing relationship (stop sharing with someone)"""
    share = TodoShare.query.filter_by(id=share_id, owner_id=current_user.id).first()
    
    if not share:
        flash('Sharing relationship not found.', 'error')
        return redirect(url_for('sharing'))
    
    shared_user = share.shared_with
    db.session.delete(share)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    flash(f'Stopped sharing todos with {shared_user.fullname or shared_user.username}.', 'success')
    return redirect(url_for('sharing'))


@app.route('/share/remove/<int:share_id>', methods=['POST'])
@login_required
def remove_share_access(share_id):
    """Remove someone's shared access to your view (they shared with you, you remove it)"""
    share = TodoShare.query.filter_by(id=share_id, shared_with_id=current_user.id).first()
    
    if not share:
        flash('Sharing relationship not found.', 'error')
        return redirect(url_for('sharing'))
    
    owner = share.owner
    db.session.delete(share)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    flash(f'Removed shared access from {owner.fullname or owner.username}.', 'success')
    return redirect(url_for('sharing'))


@app.route('/shared')
@login_required
def shared_todos():
    """View todos shared with the current user"""
    # Get users who share their todos with current user
    shared_users = TodoShare.get_shared_users(current_user.id)
    
    if not shared_users:
        return render_template('shared_todos.html', 
                              title='Shared Todos',
                              shared_todos=[],
                              shared_users=[])
    
    # Get shared user IDs for efficient query
    shared_user_ids = [u.id for u in shared_users]
    
    # Get all todos from shared users with their latest tracker in one optimized query
    # This uses a subquery to get the latest tracker timestamp for each todo
    from sqlalchemy import func
    
    # Subquery to get latest tracker timestamp for each todo
    latest_tracker_subq = db.session.query(  # type: ignore[attr-defined]
        Tracker.todo_id,
        func.max(Tracker.timestamp).label('max_timestamp')
    ).group_by(Tracker.todo_id).subquery()
    
    # Main query joining todos with their latest tracker and status
    results = db.session.query(Todo, Tracker, Status, User).join(  # type: ignore[attr-defined]
        latest_tracker_subq,
        Todo.id == latest_tracker_subq.c.todo_id
    ).join(
        Tracker,
        (Tracker.todo_id == Todo.id) & (Tracker.timestamp == latest_tracker_subq.c.max_timestamp)
    ).join(
        Status,
        Tracker.status_id == Status.id
    ).join(
        User,
        Todo.user_id == User.id
    ).filter(
        Todo.user_id.in_(shared_user_ids)
    ).order_by(Todo.modified.desc()).all()
    
    # Build the list from results
    shared_todos_list = []
    for todo, tracker, status, owner in results:
        shared_todos_list.append({
            'todo': todo,
            'owner': owner,
            'status': status.name if status else 'unknown',
            'tracker': tracker
        })
    
    return render_template('shared_todos.html', 
                          title='Shared Todos',
                          shared_todos=shared_todos_list,
                          shared_users=shared_users)


# ==================== Admin Routes ====================

def require_admin(f):
    """Decorator to require admin privileges for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_system_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@login_required
@require_admin
def admin_panel():
    """Admin panel - list all users"""
    users = User.query.all()
    return render_template('admin/panel.html', 
                          title='Admin Panel',
                          users=users)


def is_protected_admin(user):
    """Check if user is a protected admin (user without email - cannot be blocked/deleted)"""
    return user.email is None or user.email == ''


@app.route('/admin/user/<int:user_id>/block', methods=['POST'])
@login_required
@require_admin
def admin_block_user(user_id):
    """Block or unblock a user"""
    user = User.query.get_or_404(user_id)
    
    # Cannot block yourself
    if user.id == current_user.id:
        flash('You cannot block yourself.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Cannot block protected admins (users without email)
    if is_protected_admin(user):
        flash('You cannot block system administrators without email.', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_blocked = not user.is_blocked
    db.session.commit()  # type: ignore[attr-defined]
    
    action = 'blocked' if user.is_blocked else 'unblocked'
    label = user.fullname or user.email
    flash(f'User "{label}" has been {action}.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@require_admin
def admin_delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Cannot delete protected admins (users without email)
    if is_protected_admin(user):
        flash('You cannot delete system administrators without email.', 'error')
        return redirect(url_for('admin_panel'))
    
    label = user.fullname or user.email
    
    # Delete user's todos and related data
    # First delete trackers for user's todos
    user_todo_ids = [t.id for t in user.todo.all()]
    if user_todo_ids:
        Tracker.query.filter(Tracker.todo_id.in_(user_todo_ids)).delete(synchronize_session=False)
    
    # Delete user's todos
    Todo.query.filter_by(user_id=user.id).delete()
    
    # Delete sharing relationships
    TodoShare.query.filter(
        or_(TodoShare.owner_id == user.id, TodoShare.shared_with_id == user.id)
    ).delete(synchronize_session=False)
    
    # Delete share invitations (only include email condition if user has email)
    if user.email:
        ShareInvitation.query.filter(
            or_(ShareInvitation.from_user_id == user.id, ShareInvitation.to_email == user.email)
        ).delete(synchronize_session=False)
    else:
        ShareInvitation.query.filter(ShareInvitation.from_user_id == user.id).delete(synchronize_session=False)
    
    # Delete the user
    db.session.delete(user)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    flash(f'User "{label}" and all their data have been deleted.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@require_admin
def admin_toggle_admin(user_id):
    """Toggle admin status for a user with email"""
    user = User.query.get_or_404(user_id)
    
    # Cannot change your own admin status
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Only users with email can have their admin status toggled
    if user.email is None or user.email == '':
        flash('Users without email are always administrators and cannot be demoted.', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_admin = not user.is_admin
    db.session.commit()  # type: ignore[attr-defined]
    
    action = 'granted admin privileges' if user.is_admin else 'removed from administrators'
    label = user.fullname or user.email
    flash(f'User "{label}" has been {action}.', 'success')
    return redirect(url_for('admin_panel'))
