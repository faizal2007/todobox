# TodoBox - Project Overview

## Description

TodoBox (formerly MySandbox) is a Flask-based web application for managing personal todo lists. It's designed as a learning project that demonstrates Flask best practices, user authentication, database management, and task tracking functionality.

## Key Features

### Authentication & User Management

- User registration and login system
- Password hashing with Werkzeug security
- Session management with 2-hour timeout
- Remember me functionality
- Secure password change functionality

### Todo Management

- Create and edit todo items
- Organize tasks by status (new, done, failed, re-assign, kiv)
- KIV (Keep In View) status for tasks on hold or requiring future attention
- Markdown support for task descriptions
- Task scheduling (today or tomorrow)
- Task deletion
- Separate view for KIV tasks on Undone page

### Task Tracking

- Track task status changes over time
- View pending and completed tasks
- Filter tasks by date (today/tomorrow)
- Timestamp-based task history

### User Account

- Update username and email
- Change password with verification
- View account settings

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Flask | 2.3.2 |
| ORM | SQLAlchemy | 1.4.17 |
| Authentication | Flask-Login | 0.6.2 |
| Form Handling | WTForms | 2.3.3 |
| Database Migrations | Alembic/Flask-Migrate | 3.0.1 |
| Password Hashing | Werkzeug | 2.3.6 |
| Web Server | Gunicorn | 20.1.0 |
| Database Support | SQLite, MySQL, PostgreSQL | - |

## Project Structure

```text
todobox/
├── app/                          # Main application package
│   ├── __init__.py              # App initialization and configuration
│   ├── config.py                # Configuration settings
│   ├── models.py                # Database models (User, Todo, Status, Tracker)
│   ├── routes.py                # Application routes and handlers
│   ├── forms.py                 # WTForms form definitions
│   ├── utils.py                 # Utility functions (momentjs)
│   ├── static/                  # Static files (CSS, JS, images)
│   │   ├── assets/              # Third-party assets
│   │   │   ├── css/             # Stylesheets
│   │   │   ├── js/              # JavaScript files
│   │   │   └── fonts/           # Font files
│   │   └── css/                 # Application CSS
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html            # Base template
│       ├── login.html           # Login page
│       ├── todo.html            # Main todo view
│       ├── list.html            # Todo list view
│       ├── view.html            # Task view
│       ├── account.html         # Account settings
│       ├── security.html        # Password change
│       └── ...
├── lib/
│   └── database.py              # Database connection utilities
├── migrations/                  # Alembic database migrations
├── todobox.py                   # Application entry point
├── requirements.txt             # Python dependencies
├── .flaskenv.example            # Environment variables template
└── docs/                        # Documentation (this directory)
```

## Architecture Pattern

The application follows the **MVC (Model-View-Controller)** pattern:

- **Models** (`app/models.py`): Database models and business logic
- **Views** (`app/templates/`): HTML templates rendered by Jinja2
- **Controllers** (`app/routes.py`): Route handlers and request processing

## Database Models

### User Model

- Manages user accounts and authentication
- Stores username, email, fullname, and password hash
- One-to-many relationship with Todo items

### Todo Model

- Represents a task/todo item
- Stores task name, description (markdown), and HTML-rendered version
- Linked to User through foreign key
- Connected to Status through Tracker relationship

### Status Model

- Defines task status types (new, done, failed, re-assign)
- Provides static seed data

### Tracker Model

- Tracks status changes and history of todo items
- Many-to-many junction table between Todo and Status
- Stores timestamp of each status change

## Security Features

- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Password Security**: Bcrypt hashing with Werkzeug
- **Session Security**: 2-hour session timeout, session refresh required
- **Authentication**: Login required decorators on protected routes
- **Input Validation**: WTForms validators on all user inputs

## External Dependencies

- **moment.js**: Client-side date/time formatting
- **Summernote**: Rich text editor
- **SimpleMDE**: Markdown editor
- **DataTables**: Data table plugin
- **FullCalendar**: Calendar widget
- **Bootstrap 4**: CSS framework

## Configuration Options

The application supports configuration through:

- `app/config.py`: Default configuration
- `.flaskenv`: Environment-specific variables
- Instance-specific `config.py`: Runtime overrides

### Supported Databases

- SQLite (default)
- MySQL
- PostgreSQL
