
from flask import render_template, request, redirect, url_for, make_response, jsonify, abort, flash, session, g, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
from app import app, db, csrf
from app.models import Todo, User, Status, Tracker, ShareInvitation, TodoShare
from app.forms import (
    LoginForm, SetupAccountForm, ChangePassword, UpdateAccount, 
    ShareInvitationForm, SharingSettingsForm, DeleteAccountForm
)
from app.oauth import generate_google_auth_url, process_google_callback
from app.email_service import (
    send_sharing_invitation, get_invitation_link, is_email_configured,
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL
)
from urllib.parse import urlparse as url_parse
from datetime import datetime, date, timedelta
from sqlalchemy import asc, desc, or_
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import json
import urllib.request
import urllib.error
import smtplib
import secrets
import markdown
from bleach import clean
from wtforms.csrf.core import CSRF
import requests
import logging

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

# Fallback local quotes (expanded for higher variety)
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
    "Think different",
    "Small steps, big gains",
    "Consistency beats intensity",
    "Prioritize what matters",
    "One task at a time",
    "Momentum starts small",
    "Plan, then execute",
    "Trim distractions",
    "Keep moving forward",
    "Progress is a process",
    "Make today count",
    "Focus on what’s next",
    "Done is better than perfect",
    "Clarity drives action",
    "Build it, then refine it",
    "Simplify to amplify",
    "Intent before effort",
    "Less noise, more work",
    "Start where you are",
    "Show up consistently",
    "Ship, learn, improve",
    "Think long-term, act today",
    "Seek momentum, not motivation",
    "Direction over speed",
    "Tiny wins, big outcomes",
    "Focus. Execute. Iterate.",
]

@app.route('/api/quote')
@csrf.exempt
def get_quote():
    """Return a local quote without external API calls"""
    import random
    # Try external API first (ZenQuotes), fall back to LOCAL_QUOTES on any error
    api_url = 'https://zenquotes.io/api/random'
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'TodoBox/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = resp.read()
            parsed = json.loads(data)
            # ZenQuotes returns a list with objects containing 'q' (quote) and 'a' (author)
            if parsed and type(parsed) == list and len(parsed) > 0:
                item = parsed[0]
                if type(item) == dict:
                    quote = item.get('q')
                    author = item.get('a')
                    if quote:
                        # Include author if present
                        return jsonify({'quote': quote, 'author': author})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError, TypeError):
        pass

    # Fallback
    fallback_quote = random.choice(LOCAL_QUOTES)
    return jsonify({'quote': fallback_quote})

@app.route('/manifest.json')
@csrf.exempt
def get_manifest():
    """Serve dynamic PWA manifest with app title from config"""
    from app.config import TITLE
    
    manifest = {
        "name": f"{TITLE} - Todo Task Manager",
        "short_name": TITLE,
        "description": "Track and manage daily todos securely.",
        "start_url": "/dashboard",
        "scope": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#ff5555",
        "categories": ["productivity"],
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/static/assets/images/favicon.ico",
                "sizes": "32x32",
                "type": "image/x-icon"
            },
            {
                "src": "/static/assets/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icons/icon-256x256.png",
                "sizes": "256x256",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icons/icon-384x384.png",
                "sizes": "384x384",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    
    response = make_response(jsonify(manifest))
    response.headers['Content-Type'] = 'application/manifest+json'
    return response

@app.route('/api/reminders/check', methods=['GET'])
@login_required
def check_reminders():
    """Check for pending reminders for the current user"""
    from app.reminder_service import ReminderService
    from app.timezone_utils import convert_to_user_timezone
    
    reminders = ReminderService.get_pending_reminders(current_user.id)
    
    reminders_data = []
    for todo in reminders:
        # Convert reminder time to user's timezone
        reminder_time = todo.reminder_time
        if reminder_time:
            reminder_time = convert_to_user_timezone(reminder_time, current_user.timezone)
            reminder_time_str = reminder_time.isoformat() if reminder_time else None
        else:
            reminder_time_str = None
        
        # Check if this will be the last notification before auto-close
        notification_count = todo.reminder_notification_count or 0
        is_last_notification = (notification_count >= 2)  # This will be the 3rd notification
            
        reminders_data.append({
            'todo_id': todo.id,
            'title': todo.name,
            'details': todo.details,
            'reminder_time': reminder_time_str,
            'notification_count': notification_count,
            'is_last_notification': is_last_notification
        })
    
    return jsonify({
        'count': len(reminders_data),
        'reminders': reminders_data
    })

@app.route('/api/reminders/process', methods=['POST'])
@login_required
def process_reminders():
    """Process and send reminders for the current user"""
    from app.reminder_service import ReminderService
    from app.timezone_utils import convert_to_user_timezone
    
    reminders = ReminderService.get_pending_reminders(current_user.id)
    
    notifications = []
    for todo in reminders:
        # Get current notification count (before incrementing)
        notification_count = (todo.reminder_notification_count or 0) + 1
        
        # Convert reminder time to user's timezone for display
        reminder_time = todo.reminder_time
        if reminder_time:
            reminder_time = convert_to_user_timezone(reminder_time, current_user.timezone)
            reminder_time_str = reminder_time.isoformat() if reminder_time else None
        else:
            reminder_time_str = None
        
        # Determine if this is the last notification (3rd notification)
        is_last_notification = (notification_count >= 3)
        
        # Build message indicating notification count
        if notification_count == 1:
            message_suffix = " (1st reminder)"
        elif notification_count == 2:
            message_suffix = " (2nd reminder)"
        elif notification_count >= 3:
            message_suffix = " (final reminder - will auto-close after this)"
        else:
            message_suffix = ""
            
        notification = {
            'todo_id': todo.id,
            'title': f"Reminder: {todo.name}",
            'message': f"Your task '{todo.name}' is due!{message_suffix}",
            'reminder_time': reminder_time_str,
            'notification_count': notification_count,
            'is_last_notification': is_last_notification
        }
        notifications.append(notification)
        ReminderService.mark_reminder_sent(todo.id)
    
    return jsonify({
        'count': len(notifications),
        'notifications': notifications
    })

@app.route('/api/reminders/<int:todo_id>/cancel', methods=['POST'])
@login_required
def cancel_reminder(todo_id):
    """Cancel a reminder for a specific todo"""
    from app.reminder_service import ReminderService
    
    # Get the todo and verify ownership
    todo = Todo.query.get_or_404(todo_id)
    
    # Verify the todo belongs to the current user
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Cancel the reminder (don't mark as sent, just disable it)
    success = ReminderService.cancel_reminder(todo_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Reminder cancelled successfully'
        })
    else:
        return jsonify({
            'error': 'Failed to cancel reminder'
        }), 400

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

@app.route('/api/todo/<int:todo_id>', methods=['GET'])
@csrf.exempt
@login_required
def get_todo(todo_id):
    """Get a specific todo by ID"""
    # Get the todo and verify ownership
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({'success': False, 'message': 'Todo not found'}), 404
    
    # Get latest status
    latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(desc(Tracker.timestamp)).first()
    status = 'pending'
    if latest_tracker:
        status_obj = Status.query.get(latest_tracker.status_id)
        if status_obj:
            status = status_obj.name
    
    # Prepare reminder data
    reminder_data = {
        'reminder_enabled': todo.reminder_enabled or False,
        'reminder_time': None,
        'reminder_type': 'custom',
        'reminder_before_minutes': 30,
        'reminder_before_unit': 'minutes'
    }
    
    if todo.reminder_enabled and todo.reminder_time:
        # Convert reminder time to user's timezone
        from app.timezone_utils import convert_to_user_timezone
        try:
            user_tz = getattr(current_user, 'timezone', 'UTC') if current_user.is_authenticated else 'UTC'
            user_time = convert_to_user_timezone(todo.reminder_time, user_tz)
            if user_time:
                # Format as YYYY-MM-DDTHH:MM for Flatpickr compatibility
                reminder_data['reminder_time'] = user_time.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            # Fallback to UTC if timezone conversion fails
            reminder_data['reminder_time'] = todo.reminder_time.strftime('%Y-%m-%dT%H:%M')
    
    # Determine schedule type
    schedule = 'today'
    custom_date = None
    
    if todo.modified:
        from datetime import date
        today = date.today()
        todo_date = todo.modified.date()
        
        if todo_date == today:
            schedule = 'today'
        elif todo_date == today.replace(day=today.day + 1):
            schedule = 'tomorrow'
        else:
            schedule = 'custom_day'
            custom_date = todo_date.isoformat()
    
    return jsonify({
        'success': True,
        'id': todo.id,
        'title': todo.name,
        'description': todo.details,
        'status': status,
        'created_at': todo.timestamp.isoformat(),
        'modified_at': todo.modified.isoformat(),
        'schedule': schedule,
        'custom_date': custom_date,
        **reminder_data
    })

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
    except Exception:
        logging.exception("Failed to initialize default data")
        # Don't let this crash the app, but log the error

# Initialize data once when app starts
# init_default_data()  # DISABLED - moved to app startup hook


@app.route('/dashboard')
@login_required
def dashboard():
    def _categorize_todos_by_period(todos, now):
        """Categorize todos by time period and status for dashboard charts"""
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = datetime(now.year, now.month, 1)
        year_start = datetime(now.year, 1, 1)

        periods = {
            'today': {'done': 0, 're-assign': 0, 'pending': 0},
            'weekly': {'done': 0, 're-assign': 0, 'pending': 0},
            'monthly': {'done': 0, 're-assign': 0, 'pending': 0},
            'yearly': {'done': 0, 're-assign': 0, 'pending': 0}
        }

        for todo in todos:
            # Get all trackers for this todo to check completion history
            todo_trackers = (
                db.session.query(Tracker, Status.name)
                .join(Status, Tracker.status_id == Status.id)
                .filter(Tracker.todo_id == todo.id)
                .order_by(Tracker.timestamp)
                .all()
            )

            if not todo_trackers:
                continue

            # Check if todo was ever completed (has 'done' status in history)
            was_ever_completed = any(status == 'done' for _, status in todo_trackers)

            # Count re-assignments in history
            reassignment_count = sum(1 for _, status in todo_trackers if status == 're-assign')

            # Determine the category
            if was_ever_completed:
                category = 'done'
            elif reassignment_count > 0:
                category = 're-assign'
            else:
                category = 'pending'

            # Categorize by time period based on modified date
            todo_date = todo.modified

            if todo_date >= today_start:
                periods['today'][category] += 1
            if todo_date >= week_start:
                periods['weekly'][category] += 1
            if todo_date >= month_start:
                periods['monthly'][category] += 1
            if todo_date >= year_start:
                periods['yearly'][category] += 1

        # Remove zero values for cleaner charts
        for period in periods:
            periods[period] = {k: v for k, v in periods[period].items() if v > 0}

        return periods
    from app.models import Todo, Tracker, Status
    from sqlalchemy import func, desc, and_
    
    now = datetime.now()
    
    # Get all todos for the current user
    all_todos: list = db.session.query(Todo).filter_by(user_id=current_user.id).all()  # type: ignore
    
    # Categorize todos by time periods
    time_period_data = _categorize_todos_by_period(all_todos, now)
    
    # Get legacy chart_segments for backward compatibility (overall stats)
    chart_segments = {'done': 0, 're-assign': 0, 'pending': 0}
    for todo in all_todos:
        # Get all trackers for this todo to check completion history
        todo_trackers = db.session.query(Tracker, Status.name).join(Status).filter(  # type: ignore
            Tracker.todo_id == todo.id  # type: ignore
        ).order_by(Tracker.timestamp).all()  # type: ignore
        
        if not todo_trackers:
            continue
        
        # Check if todo was ever completed (has 'done' status in history)
        was_ever_completed = any(status == 'done' for _, status in todo_trackers)
        
        # Count re-assignments in history
        reassignment_count = sum(1 for _, status in todo_trackers if status == 're-assign')
        
        # Categorize todo properly
        if was_ever_completed:
            chart_segments['done'] += 1
        elif reassignment_count > 0:
            chart_segments['re-assign'] += 1
        else:
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
    completed_todos_count = chart_segments.get('done', 0)
    
    if completed_todos_count > 0:
        reassignment_stats['avg_reassignments_before_completion'] = round(
            reassignment_stats['completed_after_reassignments'] / completed_todos_count, 1
        )
    else:
        reassignment_stats['avg_reassignments_before_completion'] = 0.0
    
    # Get recent undone todos for activity feed (filtered by current user and not completed)
    # Status 6 = 'done' (see Status.seed() in models.py)
    recent_todos = db.session.query(Todo).join(  # type: ignore[attr-defined]
        Tracker, Todo.id == Tracker.todo_id  # type: ignore[attr-defined]
    ).filter(
        Todo.user_id == current_user.id,
        Tracker.timestamp == Todo.modified,  # type: ignore[attr-defined]
        Tracker.status_id != 6,  # type: ignore[attr-defined]
        Tracker.status_id != 9   # Status 9 = kiv
    ).order_by(Todo.modified.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         chart_segments=chart_segments,
                         time_period_data=time_period_data,
                         recent_todos=recent_todos,
                         reassignment_stats=reassignment_stats)

@app.route('/')
def index():
    """Root route - redirect authenticated users to dashboard, others to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

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
            
            # SECURITY: Check if this email was recently deleted
            from app.models import DeletedAccount
            if DeletedAccount.is_blocked(form.email.data):
                flash('This email address was recently deleted and cannot be re-used for 7 days. Please use a different email or wait until the cooldown period expires.', 'warning')
                return render_template('setup_account.html', title='Create Account', form=form, db_error=db_error)
            
            # Create the user
            user = User(
                email=form.email.data
            )
            user.set_password(form.password.data)
            if form.fullname.data and form.fullname.data.strip():
                user.fullname = form.fullname.data.strip()
            
            # Auto-detect timezone from IP address
            from app.geolocation import detect_timezone_from_ip
            detected_tz = detect_timezone_from_ip()
            if detected_tz:
                user.timezone = detected_tz
            
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
    """Logout the current user and clear all session data"""
    # Logout the user
    logout_user()
    
    # Clear session data but preserve flashes for the success message
    keys_to_remove = [k for k in session.keys() if k not in ['_flashes']]
    for key in keys_to_remove:
        session.pop(key, None)
    
    # Set flag to force account selection on next OAuth login
    session['force_account_selection'] = True
    
    # Flash success message
    flash('You have been successfully logged out.', 'success')
    
    # Create response with redirect
    response = make_response(redirect(url_for('login')))
    
    # Clear remember_me and session cookies
    response.set_cookie('remember_token', '', expires=0, max_age=0)
    response.set_cookie('session', '', expires=0, max_age=0)
    
    # Set cache control headers to prevent back button issues
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/logout/google')
@login_required
def logout_google():
    """Logout the current user, clear session, and also sign out of Google account"""
    # Logout the user
    logout_user()
    
    # Clear session data
    keys_to_remove = [k for k in session.keys() if k not in ['_flashes']]
    for key in keys_to_remove:
        session.pop(key, None)
    
    # Set flag to force account selection on next OAuth login
    session['force_account_selection'] = True
    
    # Flash success message
    flash('You have been successfully logged out from Google.', 'success')
    
    # Create response that redirects to Google logout
    google_logout = 'https://accounts.google.com/Logout?continue=' + url_for('login', _external=True)
    response = make_response(redirect(google_logout))
    
    # Clear remember_me and session cookies
    response.set_cookie('remember_token', '', expires=0, max_age=0)
    response.set_cookie('session', '', expires=0, max_age=0)
    
    # Set cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/auth/login/google')
def oauth_login_google():
    """Redirect user to Google for authentication"""
    try:
        auth_url = generate_google_auth_url()
        return redirect(auth_url)
    except Exception as e:
        app.logger.error(f"Error generating Google OAuth URL: {str(e)}")
        flash('Google OAuth is not properly configured. Please try password login instead.', 'danger')
        return redirect(url_for('login'))

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
        flash('Authentication failed. If you recently deleted your account, please wait 7 days before re-registering with the same email.', 'warning')
        return redirect(url_for('login'))
    
    # Check if user is blocked
    if user.is_blocked:
        flash('Your account has been blocked. Please contact an administrator.', 'error')
        return redirect(url_for('login'))
    
    # Log in the user with remember=True to ensure persistent session on mobile
    login_user(user, remember=True, duration=timedelta(days=30))
    
    if is_new:
        flash(f'Welcome! Your account has been created with {user.email}', 'success')
        next_page = url_for('account')  # Redirect to account page to complete profile
    else:
        flash(f'Welcome back, {user.fullname or user.email}!', 'success')
        next_page = request.args.get('next') or url_for('dashboard')
    
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('dashboard')
    
    # Create response with explicit cache-control to ensure cookies are set properly on mobile
    response = redirect(next_page)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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

@app.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
    """Handle user account deletion with email code verification"""
    form = DeleteAccountForm()
    gratitude_message = False
    
    if request.method == 'POST':
        # Verify the code entered by the user
        code = request.form.get('delete_code')
        session_code = session.get('delete_account_code')
        
        if not session_code or code != session_code:
            flash('Invalid or expired code. Please check your email and try again.', 'error')
            return redirect(url_for('account'))
        
        # Delete user and all related data
        user = current_user
        user_email = user.email
        user_oauth_id = user.oauth_id
        todo_ids = [t.id for t in user.todo.all()]
        
        if todo_ids:
            # Delete all trackers for this user's todos
            for tid in todo_ids:
                Tracker.query.filter_by(todo_id=tid).delete()  # type: ignore[attr-defined]
            
            # Delete all todo shares (both as owner and shared with)
            TodoShare.query.filter_by(owner_id=user.id).delete()  # type: ignore[attr-defined]
            TodoShare.query.filter_by(shared_with_id=user.id).delete()  # type: ignore[attr-defined]
            
            # Delete all todos for this user
            Todo.query.filter_by(user_id=user.id).delete()  # type: ignore[attr-defined]
        
        # Record the deletion to prevent immediate re-registration
        from app.models import DeletedAccount
        deleted_record = DeletedAccount(
            email=user_email,
            oauth_id=user_oauth_id,
            cooldown_days=7  # 7-day cooldown period before email can be re-used
        )
        db.session.add(deleted_record)  # type: ignore[attr-defined]
        
        # Delete the user account itself
        db.session.delete(user)  # type: ignore[attr-defined]
        db.session.commit()  # type: ignore[attr-defined]
        
        # Store flash message and OAuth status before clearing session
        success_message = 'Your account has been successfully deleted. Thank you for using TodoBox!'
        was_oauth_user = user.oauth_provider == 'google'
        
        # Logout the user - this clears the Flask-Login session
        logout_user()
        
        # Clear specific session keys but keep flashes
        keys_to_remove = [k for k in session.keys() if k not in ['_flashes']]
        for key in keys_to_remove:
            session.pop(key, None)
        
        # CRITICAL: Force account selection on next login to prevent auto-login after deletion
        session['force_account_selection'] = True
        
        # Add flash message
        flash(success_message, 'success')
        
        # Create redirect response to login page
        response = make_response(redirect(url_for('login')))
        
        # Clear all cookies including remember_me token and session
        response.set_cookie('remember_token', '', expires=0, max_age=0, path='/')
        response.set_cookie('session', '', expires=0, max_age=0, path='/')
        
        # Set cache control headers to prevent back button issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    
    else:
        # GET request - generate and send verification code to email
        code = str(secrets.randbelow(1000000)).zfill(6)
        session['delete_account_code'] = code
        
        # Prepare and send nicely formatted HTML email with verification code
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔐 TodoBox Account Deletion Verification Code'
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = current_user.email
        
        # Create plain text version
        text_content = f'''TodoBox Account Deletion Request

Your verification code is: {code}

This code was requested for: {current_user.email}

If you did not request this code, please ignore this email. Your account will remain secure.

Best regards,
TodoBox Team'''
        
        # Create HTML version
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .code-box {{ background: white; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
        .code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: monospace; }}
        .info-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
        .email {{ color: #667eea; font-weight: bold; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }}
        .warning {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🔐 Account Deletion Request</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>We received a request to delete your TodoBox account. To proceed with the deletion, please use the verification code below:</p>
            
            <div class="code-box">
                <div style="color: #666; font-size: 14px; margin-bottom: 10px;">Your Verification Code</div>
                <div class="code">{code}</div>
            </div>
            
            <div class="info-box">
                <strong>📧 Requested by:</strong> <span class="email">{current_user.email}</span>
            </div>
            
            <p><strong>⚠️ Important:</strong></p>
            <ul>
                <li>This code is valid for this session only</li>
                <li>Enter this code on the account deletion page to confirm</li>
                <li>This action will <span class="warning">permanently delete</span> all your data</li>
            </ul>
            
            <p>If you did not request this code, please ignore this email. Your account will remain secure and no changes will be made.</p>
            
            <div class="footer">
                <p>Best regards,<br><strong>TodoBox Team</strong></p>
                <p style="color: #999;">This is an automated message, please do not reply.</p>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM_EMAIL, [current_user.email], msg.as_string())
            flash(f'A verification code has been sent to {current_user.email}. Check your inbox and enter it below to confirm account deletion.', 'info')
        except Exception as e:
            flash('Failed to send email. Please contact support.', 'error')
            logging.error(f'Email error during account deletion: {str(e)}')
        
        return redirect(url_for('account'))

@app.route('/undone')
@login_required
def undone():
    """Show all undone/pending todos across all dates"""
    # Get all todos that are not completed (status_id != 2)
    # Use a simpler approach - get all todos and filter by latest tracker status
    
    undone_todos = []
    kiv_todos = []
    all_todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.modified.desc()).all()
    
    for todo in all_todos:
        # Get the latest tracker entry for this todo
        latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(Tracker.timestamp.desc()).first()  # type: ignore[attr-defined]
        
        if latest_tracker:
            if latest_tracker.status_id != 6 and latest_tracker.status_id != 9:
                # Uncompleted tasks
                undone_todos.append((todo, latest_tracker))
            elif latest_tracker.status_id == 9:
                # KIV tasks
                kiv_todos.append((todo, latest_tracker))
    
    return render_template('undone.html', title='Undone Tasks', todos=undone_todos, kiv_todos=kiv_todos)

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

        return jsonify({
            'status': 'Success',
            'todo_id': todo.id if todo else None
        }), 200
    else:
        return jsonify({
            'status': 'Error',
            'message': 'Todo not found'
        }), 404

@app.route('/<path:todo_id>/kiv', methods=['POST'])
@login_required
def mark_kiv(todo_id):
    """Mark a todo as kiv from any page"""
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo:
        date_entry = datetime.now()
        todo.modified = date_entry
        db.session.commit()  # type: ignore[attr-defined]
        Tracker.add(todo.id, 9, date_entry)  # Status 9 = KIV

        return jsonify({
            'status': 'Success',
            'todo_id': todo.id if todo else None
        }), 200
    else:
        return jsonify({
            'status': 'Error',
            'message': 'Todo not found'
        }), 404

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
        # DEBUG: Log all form data received
        logging.debug(f"[REMINDER DEBUG] Form data received: {dict(request.form)}")
        
        getTitle = (request.form.get("title") or "").strip()
        getActivities = (request.form.get("activities") or "").strip()
        getActivities_html = clean(markdown.markdown(getActivities, extensions=['fenced_code']), 
                                   tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        
        # Handle new schedule_day parameter
        schedule_day = request.form.get("schedule_day", "today")
        custom_date = request.form.get("custom_date", "")
        
        # Handle reminder parameters
        reminder_enabled = request.form.get("reminder_enabled") == "true"
        reminder_type = request.form.get("reminder_type")
        reminder_datetime = request.form.get("reminder_datetime")
        reminder_before_minutes = request.form.get("reminder_before_minutes")
        reminder_before_unit = request.form.get("reminder_before_unit")
        
        # DEBUG: Log reminder data parsing
        logging.debug(f"[REMINDER DEBUG] Parsed reminder data:")
        logging.debug(f"  - reminder_enabled: {reminder_enabled} (raw: '{request.form.get('reminder_enabled')}')")
        logging.debug(f"  - reminder_type: {reminder_type}")
        logging.debug(f"  - reminder_datetime: {reminder_datetime}")
        logging.debug(f"  - reminder_before_minutes: {reminder_before_minutes}")
        logging.debug(f"  - reminder_before_unit: {reminder_before_unit}")
        
        # Calculate target date based on schedule selection
        if schedule_day == "tomorrow":
            target_date = datetime.now() + timedelta(days=1)
        elif schedule_day == "custom" and custom_date:
            try:
                # Parse the date and set time to current time
                parsed_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
                current_time = datetime.now().time()
                target_date = datetime.combine(parsed_date, current_time)
            except ValueError:
                target_date = datetime.now()  # Default to today if invalid date
        else:
            target_date = datetime.now()  # Default to today
        
        tomorrow = datetime.now() + timedelta(days=1)

        if getTitle == '':
            return jsonify({
                'status': 'failed',
                'msg': 'Title Required.'
            }), 400

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
            else:
                db.session.add(t)  # type: ignore[attr-defined]

            # Handle reminder setup
            if reminder_enabled and reminder_type:
                if reminder_type == "custom" and reminder_datetime:
                    try:
                        from app.timezone_utils import convert_from_user_timezone
                        # Parse datetime-local format (YYYY-MM-DDTHH:mm)
                        reminder_dt = datetime.fromisoformat(reminder_datetime)
                        # Convert from user's timezone to UTC
                        reminder_dt_utc = convert_from_user_timezone(reminder_dt, current_user.timezone)
                        t.reminder_time = reminder_dt_utc
                        t.reminder_enabled = True
                        # Initialize reminder tracking fields for new todo
                        t.reminder_sent = False
                        t.reminder_notification_count = 0
                        t.reminder_first_notification_time = None
                    except ValueError as e:
                        logging.debug(f"Invalid reminder datetime format: {reminder_datetime} - {str(e)}")
                elif reminder_type == "before" and reminder_before_minutes and reminder_before_unit:
                    try:
                        minutes = int(reminder_before_minutes)
                        # Calculate reminder time based on target_date
                        if reminder_before_unit == "minutes":
                            reminder_dt = target_date - timedelta(minutes=minutes)
                        elif reminder_before_unit == "hours":
                            reminder_dt = target_date - timedelta(hours=minutes)
                        elif reminder_before_unit == "days":
                            reminder_dt = target_date - timedelta(days=minutes)
                        else:
                            reminder_dt = target_date - timedelta(minutes=minutes)
                        
                        t.reminder_time = reminder_dt
                        t.reminder_enabled = True
                        # Initialize reminder tracking fields for new todo
                        t.reminder_sent = False
                        t.reminder_notification_count = 0
                        t.reminder_first_notification_time = None
                    except (ValueError, TypeError):
                        logging.debug("Invalid reminder before parameters")

            db.session.commit()  # type: ignore[attr-defined]
            
            # Add tracker entry with appropriate date
            if schedule_day == "today" and getTomorrow == 0:
                # For today, use the actual timestamp from the todo
                Tracker.add(t.id, 5, t.timestamp)  # Status 5 = new
            else:
                # For tomorrow or custom date, use the target_date
                Tracker.add(t.id, 5, target_date)  # Status 5 = new
        else:
            # Updating existing todo
            todo_id = request.form.get("todo_id")
            byPass = request.form.get("byPass")
            # Filter by user_id to ensure user can only update their own todos
            t = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
            if not t:
                return jsonify({
                    'status': 'failed',
                    'msg': 'Todo not found or access denied.'
                }), 404
            title = t.name
            activites = t.details

            # Handle reminder updates
            if reminder_enabled and reminder_type:
                logging.debug(f"[REMINDER DEBUG] Processing reminder update for todo {todo_id}")
                logging.debug(f"  - reminder_enabled: {reminder_enabled}")
                logging.debug(f"  - reminder_type: {reminder_type}")
                
                if reminder_type == "custom" and reminder_datetime:
                    try:
                        logging.debug(f"  - Processing custom reminder_datetime: {reminder_datetime}")
                        from app.timezone_utils import convert_from_user_timezone
                        reminder_dt = datetime.fromisoformat(reminder_datetime)
                        logging.debug(f"  - Parsed datetime: {reminder_dt}")
                        # Convert from user's timezone to UTC
                        reminder_dt_utc = convert_from_user_timezone(reminder_dt, current_user.timezone)
                        logging.debug(f"  - Converted to UTC: {reminder_dt_utc}")
                        
                        # Store old values for comparison
                        old_time = t.reminder_time
                        old_enabled = t.reminder_enabled
                        
                        t.reminder_time = reminder_dt_utc
                        t.reminder_enabled = True
                        # Reset reminder tracking fields so the new reminder will trigger
                        t.reminder_sent = False
                        t.reminder_notification_count = 0
                        t.reminder_first_notification_time = None
                        
                        logging.debug(f"  - Updated reminder_time: {old_time} -> {reminder_dt_utc}")
                        logging.debug(f"  - Updated reminder_enabled: {old_enabled} -> True")
                        logging.debug(f"  - Reset reminder tracking fields")
                        
                    except ValueError as e:
                        logging.debug(f"Failed to parse reminder datetime: {reminder_datetime} - {str(e)}")
                elif reminder_type == "before" and reminder_before_minutes and reminder_before_unit:
                    try:
                        minutes = int(reminder_before_minutes)
                        if reminder_before_unit == "minutes":
                            reminder_dt = target_date - timedelta(minutes=minutes)
                        elif reminder_before_unit == "hours":
                            reminder_dt = target_date - timedelta(hours=minutes)
                        elif reminder_before_unit == "days":
                            reminder_dt = target_date - timedelta(days=minutes)
                        else:
                            reminder_dt = target_date - timedelta(minutes=minutes)
                        
                        t.reminder_time = reminder_dt
                        t.reminder_enabled = True
                        # Reset reminder tracking fields so the new reminder will trigger
                        t.reminder_sent = False
                        t.reminder_notification_count = 0
                        t.reminder_first_notification_time = None
                    except (ValueError, TypeError):
                        logging.debug("Failed to parse reminder before parameters")
            else:
                # Clear reminder if disabled
                t.reminder_enabled = False
                t.reminder_time = None
                t.reminder_sent = False
                t.reminder_notification_count = 0
                t.reminder_first_notification_time = None

            if getTitle == title and getActivities == activites :
                if schedule_day != "today" or getTomorrow == '1':
                    # For tomorrow or custom date, use target_date
                    t.modified = target_date
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 8, target_date)  # Status 8 = re-assign
                elif byPass == '1':
                    logging.debug(f"[REMINDER DEBUG] Taking byPass path for todo {todo_id}")
                    t.modified = datetime.now()
                    db.session.commit()  # type: ignore[attr-defined]
                    logging.debug(f"[REMINDER DEBUG] byPass commit successful for todo {todo_id}")
                else:
                    # Check if the todo's current date is different from today
                    # If so, reschedule it to today
                    if t.modified.date() != datetime.now().date():
                        logging.debug(f"[REMINDER DEBUG] Date mismatch path for todo {todo_id}")
                        t.modified = datetime.now()
                        db.session.commit()  # type: ignore[attr-defined]
                        Tracker.add(todo_id, 8, datetime.now())  # Status 8 = re-assign
                        logging.debug(f"[REMINDER DEBUG] Date mismatch commit successful, returning success")
                        return jsonify({
                            'status': 'success'
                        }), 200
                    else:
                        # Even if title/content didn't change, we still need to save reminder changes
                        logging.debug(f"[REMINDER DEBUG] Same date path for todo {todo_id} - committing reminder changes")
                        db.session.commit()  # type: ignore[attr-defined]
                        logging.debug(f"[REMINDER DEBUG] Reminder-only commit successful, returning success")
                        return jsonify({
                            'status': 'success'
                        }), 200
            else:
                t.name = getTitle
                t.details = getActivities
                t.details_html = getActivities_html
                if schedule_day != "today" or getTomorrow == '1':
                    # For tomorrow or custom date, use target_date
                    t.modified = target_date
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 8, target_date)  # Status 8 = re-assign
                else:
                    t.modified = datetime.now()
                    db.session.commit()  # type: ignore[attr-defined]
                    Tracker.add(todo_id, 5, datetime.now())  # Status 5 = new
                
                return jsonify({
                    'status': 'success'
                }), 200


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

        # Convert reminder time to user's timezone for display in the form
        reminder_time_display = None
        if t.reminder_time:
            from app.timezone_utils import convert_to_user_timezone
            reminder_dt_user = convert_to_user_timezone(t.reminder_time, current_user.timezone)
            # Format as YYYY-MM-DDTHH:MM for Flatpickr compatibility
            reminder_time_display = reminder_dt_user.strftime('%Y-%m-%dT%H:%M') if reminder_dt_user else None
        
        return jsonify({
            'status': 'Success',
            'id': t.id,
            'title': t.name,
            'activities': t.details,
            'modified': t.modified,
            'button': button,
            'reminder_enabled': t.reminder_enabled or False,
            'reminder_time': reminder_time_display,
            'reminder_sent': t.reminder_sent or False
        }), 200
    return redirect(url_for('list', id='today'))

@app.route('/<path:id>/list')
@login_required
def list(id):
   
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
        
    return render_template('list.html', title=id, todo=Todo.getList(id, start, end, user_id=current_user.id).order_by(desc(Tracker.timestamp)))  # type: ignore[arg-type]

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

        return jsonify({
            'status': 'Success',
            'todo_id': todo.id
        }), 200
    else:
        return jsonify({
            'status': 'Error',
            'message': 'Invalid list type'
        }), 400

@app.route('/<path:id>/<path:todo_id>/kiv', methods=['POST'])
@login_required
def kiv(id, todo_id):
    # Filter by user_id to ensure user can only mark their own todos as kiv
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
        Tracker.add(todo.id, 9, date_entry)  # Status 9 = KIV

        return jsonify({
            'status': 'Success',
            'todo_id': todo.id
        }), 200
    else:
        return jsonify({
            'status': 'Error',
            'message': 'Invalid list type'
        }), 400

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
    
    # Handle timezone update
    if request.method == 'POST' and 'update_timezone' in request.form:
        timezone = request.form.get('timezone', 'UTC')
        # Validate timezone is in a reasonable format (prevent injection)
        valid_timezones = [
            'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 
            'America/Los_Angeles', 'America/Anchorage', 'Pacific/Honolulu',
            'America/Toronto', 'America/Mexico_City', 'America/Buenos_Aires',
            'America/Sao_Paulo', 'Europe/London', 'Europe/Paris', 'Europe/Berlin',
            'Europe/Madrid', 'Europe/Rome', 'Europe/Amsterdam', 'Europe/Brussels',
            'Europe/Vienna', 'Europe/Prague', 'Europe/Budapest', 'Europe/Istanbul',
            'Europe/Moscow', 'Asia/Dubai', 'Asia/Kolkata', 'Asia/Bangkok',
            'Asia/Singapore', 'Asia/Hong_Kong', 'Asia/Shanghai', 'Asia/Tokyo',
            'Asia/Seoul', 'Australia/Sydney', 'Asia/Kuala_Lumpur', 'Africa/Cairo',
            'Africa/Johannesburg', 'Africa/Lagos', 'Pacific/Auckland', 'Pacific/Fiji'
        ]
        
        if timezone in valid_timezones:
            current_user.timezone = timezone
            db.session.commit()  # type: ignore[attr-defined]
            flash(f'Timezone updated to {timezone}', 'success')
        else:
            flash('Invalid timezone selected.', 'error')
        return redirect(url_for('settings'))
    
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
            to_email = (invitation_form.email.data or '').lower().strip()  # type: ignore[union-attr]
            
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
    ).order_by(desc(ShareInvitation.created_at)).limit(10).all()  # type: ignore[arg-type]
    
    # Get received invitations (pending and not expired) - use database filter for efficiency
    received_invitations = ShareInvitation.query.filter(
        ShareInvitation.to_email == current_user.email,  # type: ignore[assignment]
        ShareInvitation.status == 'pending',  # type: ignore[assignment]
        ShareInvitation.expires_at > datetime.now()  # type: ignore[assignment]
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
    flash(f'You can now see todos shared by {from_user.fullname or from_user.email}!', 'success')
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
    
    flash(f'Stopped sharing todos with {shared_user.fullname or shared_user.email}.', 'success')
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
    
    flash(f'Removed shared access from {owner.fullname or owner.email}.', 'success')
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
        Tracker.todo_id,  # type: ignore[attr-defined]
        func.max(Tracker.timestamp).label('max_timestamp')  # type: ignore[attr-defined]
    ).group_by(Tracker.todo_id).subquery()  # type: ignore[attr-defined]
    
    # Main query joining todos with their latest tracker and status
    results = db.session.query(Todo, Tracker, Status, User).join(  # type: ignore[attr-defined]
        latest_tracker_subq,
        Todo.id == latest_tracker_subq.c.todo_id
    ).join(
        Tracker,
        (Tracker.todo_id == Todo.id) & (Tracker.timestamp == latest_tracker_subq.c.max_timestamp)  # type: ignore[attr-defined]
    ).join(
        Status,
        Tracker.status_id == Status.id  # type: ignore[attr-defined]
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
    user_email = user.email
    user_oauth_id = user.oauth_id
    
    # Delete user's todos and related data
    # First delete trackers for user's todos
    user_todo_ids = [t.id for t in user.todo.all()]
    if user_todo_ids:
        Tracker.query.filter(Tracker.todo_id.in_(user_todo_ids)).delete(synchronize_session=False)  # type: ignore[attr-defined]
    
    # Delete user's todos
    Todo.query.filter_by(user_id=user.id).delete()
    
    # Delete sharing relationships
    TodoShare.query.filter(
        or_(TodoShare.owner_id == user.id, TodoShare.shared_with_id == user.id)  # type: ignore[attr-defined]
    ).delete(synchronize_session=False)
    
    # Delete share invitations (only include email condition if user has email)
    if user.email:
        ShareInvitation.query.filter(
            or_(ShareInvitation.from_user_id == user.id, ShareInvitation.to_email == user.email)  # type: ignore[attr-defined]
        ).delete(synchronize_session=False)
    else:
        ShareInvitation.query.filter(ShareInvitation.from_user_id == user.id).delete(synchronize_session=False)  # type: ignore[attr-defined]
    
    # Record the deletion to prevent immediate re-registration
    from app.models import DeletedAccount
    deleted_record = DeletedAccount(
        email=user_email,
        oauth_id=user_oauth_id,
        cooldown_days=7  # 7-day cooldown period before email can be re-used
    )
    db.session.add(deleted_record)  # type: ignore[attr-defined]
    
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


@app.route('/admin/blocked-accounts')
@login_required
@require_admin
def admin_blocked_accounts():
    """View all blocked (deleted) accounts in cooldown period"""
    from app.models import DeletedAccount
    from datetime import datetime
    
    # Get all accounts still in cooldown
    now = datetime.utcnow()
    blocked_accounts = DeletedAccount.query.filter(
        DeletedAccount.cooldown_until > now
    ).order_by(DeletedAccount.deleted_at.desc()).all()
    
    # Get expired accounts for informational purposes
    expired_accounts = DeletedAccount.query.filter(
        DeletedAccount.cooldown_until <= now
    ).order_by(DeletedAccount.deleted_at.desc()).limit(10).all()
    
    return render_template('admin/blocked_accounts.html',
                          title='Blocked Accounts',
                          blocked_accounts=blocked_accounts,
                          expired_accounts=expired_accounts)


@app.route('/admin/blocked-account/<int:account_id>/remove', methods=['POST'])
@login_required
@require_admin
def admin_remove_block(account_id):
    """Remove a block/cooldown from a deleted account"""
    from app.models import DeletedAccount
    
    blocked_account = DeletedAccount.query.get_or_404(account_id)
    email = blocked_account.email
    
    # Delete the blocked account record
    db.session.delete(blocked_account)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
    
    flash(f'Cooldown removed for "{email}". This email can now be re-registered immediately.', 'success')
    return redirect(url_for('admin_blocked_accounts'))


@app.route('/admin/blocked-accounts/cleanup', methods=['POST'])
@login_required
@require_admin
def admin_cleanup_expired_blocks():
    """Clean up all expired cooldown records"""
    from app.models import DeletedAccount
    
    count = DeletedAccount.cleanup_expired()
    flash(f'Cleaned up {count} expired cooldown records.', 'success')
    return redirect(url_for('admin_blocked_accounts'))
