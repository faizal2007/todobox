# Project Architecture

## High-Level Architecture

```

┌─────────────────────────────────────────────────────────────┐
│                      Browser (Client)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                   HTTP Requests/Responses
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Route Handlers (routes.py)            │  │
│  │  - /login, /logout                                 │  │
│  │  - /todo, /add, /<id>/list                         │  │
│  │  - /account, /security                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Form Validation Layer (forms.py)           │  │
│  │  - LoginForm                                       │  │
│  │  - ChangePassword, UpdateAccount                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     Authentication & Authorization (Flask-Login)   │  │
│  │  - current_user                                    │  │
│  │  - login_required decorator                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Business Logic Layer (models.py)          │  │
│  │  - User model with password management             │  │
│  │  - Todo model with queries                         │  │
│  │  - Status model with seed data                     │  │
│  │  - Tracker model for history                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Database Access Layer (SQLAlchemy ORM)       │  │
│  │  - SQL Query Generation                            │  │
│  │  - Connection Management                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User │ Todo │ Status │ Tracker (MySQL/PostgreSQL)  │  │
│  │             OR SQLite Database                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Layered Architecture

### 1. **Presentation Layer** (`app/templates/`)
Renders HTML views to the browser
- `base.html`: Base template with common layout
- `login.html`: Authentication UI
- `todo.html`, `list.html`: Todo management UI
- `account.html`, `security.html`: User settings UI

### 2. **Request Handler Layer** (`app/routes.py`)
Processes HTTP requests and coordinates responses
- Validates input from forms
- Calls business logic
- Renders templates or returns JSON
- Handles redirects and error responses

### 3. **Form Validation Layer** (`app/forms.py`)
WTForms-based validation layer
- Validates user input before processing
- Implements custom validators
- Provides CSRF protection

### 4. **Authentication Layer** (`app/__init__.py`)
Manages user authentication and sessions
- Flask-Login integration
- Session timeout (2 hours)
- Login required protection

### 5. **Business Logic Layer** (`app/models.py`)
Contains application logic and data operations
- User authentication (password hashing)
- Todo CRUD operations
- Task status tracking
- Query methods

### 6. **Data Access Layer** (`lib/database.py`)
Manages database connections and configuration
- Multi-database support (SQLite, MySQL, PostgreSQL)
- Connection string management
- Environment variable handling

### 7. **Database Layer**
Physical data storage
- SQLite (development)
- MySQL/PostgreSQL (production)

## File Structure & Responsibilities

```
mysandbox/
├── app/
│   ├── __init__.py              # App factory, configuration
│   │   ├── Create Flask app instance
│   │   ├── Configure extensions (db, migrate, csrf, login)
│   │   └── Initialize routes and models
│   │
│   ├── config.py                # Configuration constants
│   │   ├── SALT, SECRET_KEY
│   │   └── DATABASE_NAME, DATABASE_DEFAULT
│   │
│   ├── models.py                # Data models
│   │   ├── User: Authentication & account management
│   │   ├── Todo: Task items
│   │   ├── Status: Task status types
│   │   └── Tracker: Status change history
│   │
│   ├── routes.py                # Request handlers
│   │   ├── Authentication routes (login, logout)
│   │   ├── Todo CRUD routes (add, list, view, delete)
│   │   ├── User account routes (account, security)
│   │   └── AJAX endpoints (getTodo, done)
│   │
│   ├── forms.py                 # Form definitions & validation
│   │   ├── LoginForm
│   │   ├── ChangePassword
│   │   └── UpdateAccount
│   │
│   ├── utils.py                 # Utility functions
│   │   └── momentjs class (date formatting)
│   │
│   ├── static/                  # Static assets
│   │   ├── assets/              # Third-party CSS/JS
│   │   ├── css/                 # Application CSS
│   │   ├── fonts/               # Font files
│   │   └── images/              # Image assets
│   │
│   └── templates/               # Jinja2 templates
│       ├── base.html            # Master template
│       ├── login.html           # Login page
│       ├── todo.html            # Main todo view
│       ├── list.html            # Todo list view
│       ├── view.html            # Task details
│       ├── account.html         # Account settings
│       └── security.html        # Password change
│
├── lib/
│   └── database.py              # Database connection logic
│       └── Multi-database support (MySQL, PostgreSQL, SQLite)
│
├── migrations/                  # Alembic database migrations
│   ├── alembic.ini             # Migration configuration
│   ├── env.py                  # Migration environment
│   └── versions/               # Migration scripts
│
├── mysandbox.py                 # Application entry point
├── requirements.txt             # Python dependencies
├── .flaskenv.example            # Environment template
└── docs/                        # Documentation
```

## Data Flow

### Todo Creation Flow
```
1. User submits form on todo.html
   ↓
2. POST /add route handler (routes.py)
   ↓
3. Form validation (built-in Flask-WTF)
   ↓
4. Create Todo instance (models.py)
   ↓
5. db.session.add() & db.session.commit()
   ↓
6. Create Tracker entry (Status history)
   ↓
7. Return JSON response to client
   ↓
8. JavaScript updates UI
```

### User Authentication Flow
```
1. User visits / (index)
   ↓
2. Redirect to /login (if not authenticated)
   ↓
3. User submits credentials via LoginForm
   ↓
4. Query User model for username
   ↓
5. check_password() validates hash
   ↓
6. login_user() creates session
   ↓
7. Redirect to todo list
```

### Task Status Update Flow
```
1. User clicks "Done" button on todo item
   ↓
2. AJAX POST to /<id>/<todo_id>/done
   ↓
3. Update Todo.modified timestamp
   ↓
4. Create Tracker entry with status_id=2 (done)
   ↓
5. Commit to database
   ↓
6. Return JSON success response
   ↓
7. JavaScript removes item from UI
```

## Design Patterns Used

### Model-View-Controller (MVC)
- **Model**: `app/models.py` (User, Todo, Status, Tracker)
- **View**: `app/templates/` (Jinja2 templates)
- **Controller**: `app/routes.py` (Route handlers)

### Dependency Injection
- Flask app instance passed to extensions
- Database connection configured in `app/__init__.py`

### Factory Pattern
- Flask app created in `app/__init__.py`
- Extensions (db, migrate, csrf, login) configured with app

### Repository Pattern (Partial)
- Query methods in models (`Todo.getList()`)
- Methods encapsulate database logic

### Singleton Pattern
- Single Flask app instance
- Single database instance
- Single login manager instance

## Data Relationships

### Entity Relationships

```
User (1) ─────────► (Many) Todo
  │                     │
  │                     ├─ name (String)
  ├─ id                 ├─ details (String)
  ├─ username           ├─ details_html (String)
  ├─ email              ├─ timestamp
  ├─ fullname           ├─ modified
  └─ password_hash      └─ user_id (FK)
                             │
                             ▼
                    (Many) Tracker (Junction)
                             │
                             ├─ todo_id (FK)
                             ├─ status_id (FK)
                             └─ timestamp
                             │
                             ▼
                        Status (1)
                             ├─ id
                             ├─ name (new, done, failed, re-assign)
                             └─ (Many) Todos
```

## Request Processing Pipeline

```
HTTP Request
    ↓
Flask URL Routing (route matching)
    ↓
Authentication Check (login_required decorator)
    ↓
Form Validation (if POST)
    ↓
Route Handler Execution (routes.py function)
    ↓
Database Query (models.py, SQLAlchemy)
    ↓
Template Rendering or JSON Response
    ↓
HTTP Response (HTML or JSON)
```

## Configuration Management

### Configuration Sources (in order of precedence)

1. **Instance Config** (highest priority)
   - `instance/config.py`
   - Runtime overrides

2. **Environment Variables**
   - `.flaskenv` file
   - System environment variables

3. **Application Config** (lowest priority)
   - `app/config.py`
   - Default values

### Configuration Flow
```
app/config.py (base config)
    ↓
app.config.from_pyfile('config.py', silent=True)
    ↓
.flaskenv (environment variables)
    ↓
Instance config (overrides)
    ↓
Final Configuration
```

## Database Connection Flow

```
1. app/__init__.py
   ├─ Check DATABASE_DEFAULT setting
   │
   ├─ If 'mysql':
   │  └─ connect_db('mysql', app)
   │     └─ lib/database.py builds MySQL URI
   │
   ├─ If 'postgres':
   │  └─ connect_db('postgres', app)
   │     └─ lib/database.py builds PostgreSQL URI
   │
   └─ If 'sqlite':
      └─ Build SQLite URI to instance/mysandbox.db

2. SQLAlchemy initializes connection pool

3. Alembic migrations applied if needed

4. Database ready for queries
```

## Session & State Management

### Session Lifetime
```
User Login
    ↓
Session created (2 hours duration)
    ↓
Login token stored in session
    ↓
User requests protected resource
    ↓
Session validity checked
    ↓
├─ Valid: Request processed
├─ Expired: Redirect to re-login
└─ Invalid: Redirect to login
    ↓
User Logout
    ↓
Session destroyed
```

### Server-Side State
- Stored in database (persistent)
- Session data in Flask session (temporary)
- User identified by session token

## Security Architecture

```
Incoming Request
    ↓
CSRF Token Validation (csrf_protect)
    ↓
Authentication Check (login_required)
    ↓
Authorization Check (current_user validation)
    ↓
Input Validation (WTForms validators)
    ↓
SQL Injection Prevention (SQLAlchemy parameterized queries)
    ↓
Password Security (Werkzeug bcrypt hashing)
    ↓
Session Security (httponly cookies, same-site)
    ↓
Response (Safe)
```

## Performance Considerations

### Caching Opportunities
- User objects (cache after login)
- Status types (seed once, rarely change)
- Todo queries (cache for 5 minutes)

### Database Optimization
- Indexes on: username, email, timestamps
- Lazy loading vs eager loading
- Query optimization in `Todo.getList()`

### Bottlenecks
- Markdown rendering on every save
- No pagination for large todo lists
- No async operations

## Scalability Recommendations

### Horizontal Scaling
- Use MySQL/PostgreSQL (not SQLite)
- Use Gunicorn with multiple workers
- Add load balancer
- Use Redis for session store

### Vertical Scaling
- Database indexing optimization
- Query caching
- Connection pooling

### Architecture Evolution
```
Current (Single Server)
    ↓
Add Caching Layer (Redis)
    ↓
Separate Database Server
    ↓
Load Balancer + Multiple App Servers
    ↓
Microservices (Auth service, Todo service)
    ↓
Containerization (Docker + Kubernetes)
```

## Third-Party Libraries Architecture

```
Flask Framework
├─ Flask-SQLAlchemy (ORM)
├─ Flask-Migrate (Database migrations)
├─ Flask-WTF (Form handling + CSRF)
├─ Flask-Login (Authentication)
└─ Werkzeug (Security, utilities)

Frontend
├─ Bootstrap 4 (CSS framework)
├─ Summernote (Rich editor)
├─ SimpleMDE (Markdown editor)
├─ DataTables (Data tables)
├─ FullCalendar (Calendar)
├─ moment.js (Date formatting)
└─ jQuery (DOM manipulation)

Utilities
├─ Markdown (Markdown parsing)
├─ python-dotenv (Environment variables)
└─ gunicorn (Production server)
```

## Deployment Architecture Options

### Option 1: Standalone Server
```
Internet
    ↓
Nginx (reverse proxy)
    ↓
Gunicorn (WSGI server)
    ↓
Flask App
    ↓
MySQL/PostgreSQL
```

### Option 2: Containerized
```
Internet
    ↓
Nginx
    ↓
Docker Container (Flask + Gunicorn)
    ↓
External Database
```

### Option 3: Scalable
```
Internet
    ↓
Load Balancer
    ↓
├─ App Server 1 ─┐
├─ App Server 2  ├─→ Database Cluster
└─ App Server 3 ─┘
    ↓
Redis (Session Store)
```
