# Project Architecture

**Last Updated:** January 16, 2026  
**Version:** 2.0

## High-Level Architecture

```bash

┌─────────────────────────────────────────────────────────────┐
│                  Browser (Client / PWA)                     │
│  - Progressive Web App Support                              │
│  - Service Worker for Offline Caching                       │
│  - Responsive UI (Bootstrap 4)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                   HTTP/HTTPS Requests/Responses
                   API Token Authentication (Bearer)
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Route Handlers (routes.py - 155KB)         │  │
│  │  - Authentication: /login, /logout, /register      │  │
│  │  - OAuth: /auth/google, /auth/callback            │  │
│  │  - Todos: /add, /list, /dashboard, /achievements  │  │
│  │  - Sharing: /sharing, /shared-todos                │  │
│  │  - API: /api/todo, /api/reminders, /api/quote      │  │
│  │  - Admin: /admin/panel, /admin/blocked-accounts   │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Form Validation Layer (forms.py)           │  │
│  │  - LoginForm, RegistrationForm                     │  │
│  │  - SimpleTodoForm, AdvancedTodoForm                │  │
│  │  - ChangePassword, UpdateAccount                   │  │
│  │  - DeleteAccountForm                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Security & Authentication Layer            │  │
│  │  - Flask-Login (session management)                │  │
│  │  - OAuth (Google Sign-In)                          │  │
│  │  - API Token Authentication                        │  │
│  │  - Email Verification (verification.py)            │  │
│  │  - Encryption Service (encryption.py - Fernet)     │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Business Logic Layer (models.py)          │  │
│  │  - User (OAuth, email verification, API tokens)    │  │
│  │  - Todo (encrypted data, reminders, types)         │  │
│  │  - Status, Tracker (status history)                │  │
│  │  - KIV (Keep In View tracking)                     │  │
│  │  - ShareInvitation, TodoShare (sharing)            │  │
│  │  - DeletedAccount, TermsAndDisclaimer              │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Service Layer (New Services)            │  │
│  │  - ReminderService: Notification scheduling        │  │
│  │  - EmailService: SMTP email delivery               │  │
│  │  - GeolocationService: IP-based timezone detection │  │
│  │  - TimezoneUtils: Timezone conversion              │  │
│  │  - EncryptionService: Data protection              │  │
│  │  - VerificationService: Token generation           │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Database Access Layer (SQLAlchemy ORM)       │  │
│  │  - SQL Query Generation                            │  │
│  │  - Connection Management                           │  │
│  │  - Multi-DB Support (SQLite/MySQL/PostgreSQL)     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 9 Tables: User, Todo, Status, Tracker, KIV,        │  │
│  │ ShareInvitation, TodoShare, DeletedAccount,        │  │
│  │ TermsAndDisclaimer                                 │  │
│  │ Backend: MySQL/PostgreSQL/SQLite                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Layered Architecture

### 1. Presentation Layer (`app/templates/`)

Renders HTML views to the browser with PWA support

**Core Templates:**
- `base.html`: Master template with navigation, PWA manifest
- `main.html`: Dashboard with donut charts, recent todos, PWA install button
- `login.html`, `register.html`: Authentication and registration UI
- `setup_wizard.html`: 5-step initial setup guide

**Todo Management:**
- `list.html`: Today/tomorrow todo lists with grid layout
- `undone.html`: Uncompleted tasks and KIV tab
- `achievements.html`: Completed todos with infinite scroll

**User Management:**
- `account.html`: Profile settings, account deletion
- `settings.html`: Password change, API token management
- `sharing.html`: Todo sharing with other users
- `shared_todos.html`: View shared todos from others

**Admin:**
- `admin/panel.html`: User management, system administration
- `admin/terms.html`: Terms and disclaimer management
- `admin/blocked_accounts.html`: Deleted account cooldown management

### 2. Request Handler Layer (`app/routes.py` - 155KB)

Processes HTTP requests and coordinates responses

**Authentication Routes:**
- `/login`, `/logout`, `/register`
- `/verify-email/<token>`, `/resend-verification`
- `/auth/google`, `/auth/callback/google` (OAuth)

**Todo Management:**
- `/add`, `/add_simple` (Simple vs Advanced mode)
- `/today/list`, `/tomorrow/list`, `/undone`
- `/dashboard`, `/achievements`
- `/<id>/todo` (edit), `/<id>/done`, `/<id>/delete`
- `/<todo_id>/kiv` (Keep In View)

**Sharing & Collaboration:**
- `/sharing` (manage sharing)
- `/shared-todos` (view shared todos)
- `/share/invite/<token>` (accept invitation)

**API Endpoints:**
- `/api/todo` (CRUD with Bearer token auth)
- `/api/auth/token` (generate API token)
- `/api/reminders/check`, `/api/reminders/process`
- `/api/quote` (wisdom quotes)
- `/api/achievements/batch` (infinite scroll)

**Admin Routes:**
- `/admin/panel`, `/admin/delete-user/<id>`
- `/admin/terms` (manage terms and disclaimer)
- `/admin/blocked-accounts` (cooldown management)

### 3. Form Validation Layer (`app/forms.py`)

WTForms-based validation with custom validators

**Authentication Forms:**
- `LoginForm`: Email and password validation
- `RegistrationForm`: Email uniqueness, password confirmation, terms acceptance

**Todo Forms:**
- `SimpleTodoForm`: Title-only quick creation
- `AdvancedTodoForm`: Rich markdown content

**User Management:**
- `ChangePassword`: Password validation for direct login users
- `UpdateAccount`: Profile information updates
- `DeleteAccountForm`: Account deletion verification code

### 4. Security & Authentication Layer

Multi-layered authentication and security

**Session Management (`app/__init__.py`):**
- Flask-Login integration
- Session timeout (2 hours)
- Remember me functionality
- Force account selection after logout

**OAuth Integration (`app/oauth.py`):**
- Google Sign-In (OAuth 2.0)
- Automatic account creation
- Proxy-aware redirect URI handling
- Terms acceptance requirement

**Email Verification (`app/verification.py`):**
- Token generation (24-hour expiration)
- Secure URL-safe tokens
- Email verification requirement for registration

**Data Encryption (`app/encryption.py`):**
- Fernet symmetric encryption
- PBKDF2 key derivation from SECRET_KEY
- Optional encryption for todo data (title, details)
- Protection from database administrators

**API Authentication:**
- Bearer token authentication
- API token generation and management
- Token-based access to REST API

### 5. Business Logic Layer (`app/models.py` - 26KB)

Contains application logic and data operations with 9 models

**User Model:**
- OAuth and password authentication
- Email verification status
- API token management
- Timezone support
- Admin and blocked user flags
- Terms acceptance tracking
- Sharing preferences (Gmail users only)

**Todo Model:**
- Encrypted data storage (name, details, details_html)
- Todo types: Simple (checklists) and Advanced (markdown)
- Reminder system with notification tracking
- Target date and modified timestamp
- Auto-close reminders after 3 notifications

**Status Model:**
- Task statuses: new (5), done (6), failed (7), re-assign (8)
- Seed data initialization

**Tracker Model:**
- Status change history
- Timestamp tracking
- Cascading delete with KIV

**KIV Model (Keep In View):**
- Separate table for KIV todos
- Active/inactive status
- Entry and exit timestamps

**ShareInvitation Model:**
- Pending sharing invitations
- Token-based approval
- 7-day expiration
- Status tracking (pending, accepted, declined, expired)

**TodoShare Model:**
- Todo sharing relationships between users
- Owner and shared_with tracking
- Unique constraint per user pair

**DeletedAccount Model:**
- 7-day cooldown period after deletion
- Prevents immediate re-registration
- Email and OAuth ID tracking

**TermsAndDisclaimer Model:**
- Versioned terms of service
- Admin management
- Active/inactive versions

### 6. Service Layer (New in v2.0)

Business logic extracted into specialized services

**ReminderService (`app/reminder_service.py`):**
- Scheduled notification checks
- 30-minute interval enforcement
- Auto-close after 3 reminders within 30 minutes
- Notification count tracking

**EmailService (`app/email_service.py`):**
- SMTP email delivery
- Sharing invitation emails
- Verification code emails
- HTML email templates
- 14+ anti-spam headers

**GeolocationService (`app/geolocation.py`):**
- IP-based timezone detection
- ipapi.co integration
- Automatic timezone assignment for new users

**TimezoneUtils (`app/timezone_utils.py`):**
- Timezone conversion utilities
- 43+ timezone options
- UTC to user timezone conversion

**EncryptionService (`app/encryption.py`):**
- Fernet symmetric encryption
- Key derivation from SECRET_KEY
- Encrypt/decrypt utilities
- Optional encryption toggle

**VerificationService (`app/verification.py`):**
- Secure token generation
- Email verification tokens
- 24-hour expiration
- URL-safe token encoding

### 7. Data Access Layer (`lib/database.py`)

Manages database connections and configuration

- Multi-database support (SQLite, MySQL, PostgreSQL)
- Connection string management
- Environment variable handling
- Dynamic database selection

### 8. Database Layer

Physical data storage with migration support

**Development:**
- SQLite (instance/todobox.db)
- Auto-created on first run

**Production:**
- MySQL 5.7+ (verified with 192.168.1.112:3306)
- PostgreSQL (optional)
- Alembic migrations in `migrations/versions/`

---

## Database Configuration (Updated November 2025)

### Supported Databases

The application supports three database backends via environment configuration:

```text
DATABASE_DEFAULT=sqlite     (Default) - SQLite development database
DATABASE_DEFAULT=mysql      - MySQL 5.7+ production database
DATABASE_DEFAULT=postgres   - PostgreSQL production database
```

### Database Selection Logic

```python
# From app/__init__.py
if app.config['DATABASE_DEFAULT'] == 'mysql':
    connect_db('mysql', app)           # Use MySQL
elif app.config['DATABASE_DEFAULT'] == 'postgres':
    connect_db('postgres', app)        # Use PostgreSQL
else:
    # SQLite fallback (default if DATABASE_DEFAULT not set)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/todobox.db'
```

### SQLite Configuration

- **Default** choice for development
- Database file: `instance/todobox.db`
- **No setup required** - database created automatically on first migration
- Ideal for: Learning, testing, single-user development
- Instance folder created automatically when using SQLite

### MySQL Configuration (Current Production)

- Configured via `.flaskenv` (192.168.1.112 - shimasu_db)
- Connection string: `mysql+mysqldb://user:password@host:port/database`
- **Database must be created manually** before running migrations
- Ideal for: Production, multi-user scenarios, team development

**Environment Variables:**

```bash
DATABASE_DEFAULT=mysql
DB_URL=192.168.1.112
DB_USER=freakie
DB_PASSWORD=md711964
DB_NAME=shimasu_db
```

### PostgreSQL Configuration

- Connection string: `postgresql://user:password@host:port/database`
- Similar setup to MySQL
- Ideal for: Advanced queries, better transaction handling

**Environment Variables:**

```bash
DATABASE_DEFAULT=postgres
DB_URL=localhost
DB_USER=todobox
DB_PASSWORD=password
DB_NAME=todobox
```

### Instance Folder Status

- **Purpose**: Local development data storage (SQLite only)
- **Contents**: SQLite database file, local config overrides
- **Git Status**: Not version controlled (in .gitignore)
- **When Used**: Only when `DATABASE_DEFAULT=sqlite` (or unset)
- **When NOT Used**: When `DATABASE_DEFAULT=mysql` or `DATABASE_DEFAULT=postgres`

**Status as of November 2025:**

- ✅ Instance folder not created when MySQL configured
- ✅ No SQLite database in use when `DATABASE_DEFAULT=mysql`
- ✅ Multi-database support verified working
- ✅ MySQL connection established (192.168.1.112:3306)

---

## File Structure & Responsibilities

```bash
todobox/
├── app/
│   ├── __init__.py              # App factory, extensions, configuration (9KB)
│   │   ├── Create Flask app instance
│   │   ├── Configure extensions (db, migrate, csrf, login, mail)
│   │   ├── ProxyFix middleware for reverse proxy support
│   │   ├── Security headers (CSP, X-Frame-Options, etc.)
│   │   └── Initialize routes, models, and services
│   │
│   ├── config.py                # Configuration constants (3.5KB)
│   │   ├── SALT, SECRET_KEY (auto-generated)
│   │   ├── DATABASE_NAME, DATABASE_DEFAULT
│   │   ├── SMTP configuration
│   │   ├── OAuth configuration (Google)
│   │   ├── TODO_ENCRYPTION_ENABLED toggle
│   │   └── Proxy configuration (X-Forwarded headers)
│   │
│   ├── models.py                # Data models (26KB, 9 models)
│   │   ├── User: Authentication, OAuth, email verification, API tokens
│   │   ├── Todo: Encrypted data, reminders, types (simple/advanced)
│   │   ├── Status: Task status types (new, done, failed, re-assign)
│   │   ├── Tracker: Status change history
│   │   ├── KIV: Keep In View tracking
│   │   ├── ShareInvitation: Sharing invitation tokens
│   │   ├── TodoShare: Todo sharing relationships
│   │   ├── DeletedAccount: Account deletion cooldown
│   │   └── TermsAndDisclaimer: Terms of service versioning
│   │
│   ├── routes.py                # Request handlers (155KB)
│   │   ├── Authentication: login, logout, register, OAuth
│   │   ├── Email verification: verify-email, resend-verification
│   │   ├── Todo CRUD: add, add_simple, list, edit, delete
│   │   ├── Todo operations: done, kiv, toggle_item
│   │   ├── Views: dashboard, achievements, undone
│   │   ├── Sharing: sharing, shared-todos, invite acceptance
│   │   ├── User settings: account, settings, delete_account
│   │   ├── API endpoints: /api/todo, /api/auth/token, /api/reminders, /api/quote
│   │   └── Admin: panel, user management, terms, blocked accounts
│   │
│   ├── forms.py                 # Form definitions & validation (5.5KB)
│   │   ├── LoginForm, RegistrationForm
│   │   ├── SimpleTodoForm, AdvancedTodoForm
│   │   ├── ChangePassword, UpdateAccount
│   │   └── DeleteAccountForm
│   │
│   ├── forms/                   # Additional form modules
│   │   └── delete_account_form.py
│   │
│   ├── utils.py                 # Utility functions (4.9KB)
│   │   ├── momentjs class (date formatting)
│   │   ├── Input sanitization
│   │   └── Helper functions
│   │
│   ├── oauth.py                 # OAuth integration (5.6KB)
│   │   ├── Google OAuth configuration
│   │   ├── OAuth callback handling
│   │   ├── Proxy-aware redirect URI
│   │   └── Automatic account creation
│   │
│   ├── email_service.py         # Email delivery service (10.4KB)
│   │   ├── SMTP configuration
│   │   ├── Sharing invitation emails
│   │   ├── Verification code emails
│   │   ├── HTML email templates
│   │   └── 14+ anti-spam headers
│   │
│   ├── encryption.py            # Data encryption service (4.7KB)
│   │   ├── Fernet symmetric encryption
│   │   ├── PBKDF2 key derivation
│   │   ├── encrypt_text() / decrypt_text()
│   │   └── Optional encryption toggle
│   │
│   ├── verification.py          # Email verification (2.2KB)
│   │   ├── Token generation
│   │   ├── Token validation
│   │   └── 24-hour expiration
│   │
│   ├── reminder_service.py      # Reminder system (7.6KB)
│   │   ├── Scheduled notification checks
│   │   ├── 30-minute interval enforcement
│   │   ├── Auto-close after 3 reminders
│   │   └── Notification count tracking
│   │
│   ├── geolocation.py           # IP geolocation (4.3KB)
│   │   ├── ipapi.co integration
│   │   ├── Timezone detection from IP
│   │   └── Fallback to UTC
│   │
│   ├── timezone_utils.py        # Timezone utilities (2KB)
│   │   ├── UTC to user timezone conversion
│   │   └── 43+ timezone options
│   │
│   ├── cli.py                   # CLI commands (5.9KB)
│   │   ├── Flask CLI commands
│   │   └── Database management
│   │
│   ├── static/                  # Static assets
│   │   ├── assets/              # Third-party CSS/JS libraries
│   │   │   ├── vendor/          # Bootstrap, jQuery, DataTables
│   │   │   ├── plugins/         # SimpleMDE, Flatpickr, Chart.js
│   │   │   └── libs/            # Additional libraries
│   │   ├── css/                 # Application CSS
│   │   │   ├── style.css        # Main styles
│   │   │   ├── dashboard.css    # Dashboard-specific styles
│   │   │   └── theme-*.css      # Theme variations
│   │   ├── fonts/               # Custom font files
│   │   ├── manifest.json        # PWA manifest
│   │   └── service-worker.js    # PWA service worker (v3)
│   │
│   └── templates/               # Jinja2 templates
│       ├── base.html            # Master template with navigation
│       ├── main.html            # Dashboard with donut charts
│       ├── login.html           # Login page with OAuth
│       ├── register.html        # Registration with terms
│       ├── setup_wizard.html    # 5-step setup wizard
│       ├── list.html            # Todo list (today/tomorrow)
│       ├── undone.html          # Undone tasks + KIV tab
│       ├── achievements.html    # Completed todos
│       ├── account.html         # Account settings
│       ├── settings.html        # Password & API tokens
│       ├── sharing.html         # Todo sharing management
│       ├── shared_todos.html    # View shared todos
│       ├── todo_add.html        # Add/edit todo modal
│       ├── confirm_modal.html   # Reusable confirmation modal
│       └── admin/               # Admin templates
│           ├── panel.html       # User management
│           ├── terms.html       # Terms management
│           └── blocked_accounts.html
│
├── lib/
│   └── database.py              # Database connection logic
│       └── Multi-database support (MySQL, PostgreSQL, SQLite)
│
├── migrations/                  # Alembic database migrations
│   ├── alembic.ini             # Migration configuration
│   ├── env.py                  # Migration environment
│   └── versions/               # 30+ migration scripts
│
├── tests/                       # Test suite (227 tests, 80.6% passing)
│   ├── conftest.py             # Test fixtures
│   ├── test_models.py          # Model tests
│   ├── test_routes.py          # Route tests
│   ├── test_api.py             # API tests
│   ├── test_reminders.py       # Reminder system tests
│   └── test_regressions.py     # Regression tests
│
├── docs/                        # Documentation (50+ files)
│   ├── README.md               # Documentation index
│   ├── ARCHITECTURE.md         # This file
│   ├── MODELS.md               # Database schema
│   ├── API.md                  # API reference
│   ├── QUICKSTART.md           # Quick start guide
│   ├── SETUP.md                # Installation guide
│   └── archive/                # Archived documentation
│
├── todobox.py                   # Application entry point
├── todomanage.py                # CLI management tool
├── requirements.txt             # Python dependencies
├── .flaskenv.example            # Environment template
├── .copilot-markdown-rules.md   # Documentation standards
├── CHANGELOG.md                 # Change history
├── SECURITY.md                  # Security policy
├── LICENSE                      # MIT License
└── README.md                    # Project overview
```

## Data Flow

### Todo Creation Flow

```text
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

```text
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

```text
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

### Entity Relationships (Updated v2.0)

```bash
User (1) ─────────► (Many) Todo
  │                     │
  │                     ├─ _name (Encrypted Text)
  ├─ id                 ├─ _details (Encrypted Text)
  ├─ email              ├─ _details_html (Encrypted Text)
  ├─ fullname           ├─ timestamp, modified, target_date
  ├─ password_hash      ├─ reminder_enabled, reminder_time
  ├─ oauth_provider     ├─ reminder_notification_count
  ├─ oauth_id           ├─ todo_type (simple/advanced)
  ├─ email_verified     └─ user_id (FK)
  ├─ api_token              │
  ├─ sharing_enabled        ├──► (Many) Tracker (Status History)
  ├─ timezone               │       ├─ todo_id (FK)
  ├─ is_admin               │       ├─ status_id (FK)
  └─ terms_accepted_ver     │       └─ timestamp
                            │           │
                            │           ▼
                            │      Status (1)
                            │       ├─ id (5=new, 6=done, 7=failed, 8=re-assign)
                            │       └─ name
                            │
                            └──► (0..1) KIV (Keep In View)
                                    ├─ todo_id (FK, unique)
                                    ├─ user_id (FK)
                                    ├─ entered_at, exited_at
                                    └─ is_active

User (Owner) ──┐
               ├──► ShareInvitation (Many)
               │       ├─ from_user_id (FK)
               │       ├─ to_email
               │       ├─ token (unique)
               │       ├─ status (pending/accepted/declined/expired)
               │       └─ expires_at
               │
               └──► TodoShare (Many as owner)
                       ├─ owner_id (FK)
                       ├─ shared_with_id (FK)
                       └─ created_at
                           │
User (Viewer) ◄────────────┘

DeletedAccount (Cooldown)
  ├─ email
  ├─ oauth_id
  ├─ deleted_at
  └─ cooldown_until (7 days)

TermsAndDisclaimer (Versioned)
  ├─ version
  ├─ content
  ├─ is_active
  └─ created_at
```

## Request Processing Pipeline

```text
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

```text
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

```text
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
      └─ Build SQLite URI to instance/todobox.db

2. SQLAlchemy initializes connection pool

3. Alembic migrations applied if needed

4. Database ready for queries
```

## Session & State Management

### Session Lifetime

```text
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

## Security Architecture (Updated v2.0)

```bash
Incoming Request
    ↓
┌─────────────────────────────────────┐
│ PWA Service Worker (Cache Check)    │
│ - Offline support for static assets │
│ - External CDN bypass                │
└─────────────────────────────────────┘
    ↓
ProxyFix Middleware (Reverse Proxy Support)
    ↓
Security Headers
├─ Content-Security-Policy
├─ X-Frame-Options: DENY
├─ X-Content-Type-Options: nosniff
└─ Referrer-Policy: no-referrer
    ↓
CSRF Token Validation (csrf_protect)
├─ Exempt: API endpoints with Bearer tokens
└─ Required: All web form submissions
    ↓
Authentication Layer
├─ Session-based (Flask-Login)
├─ OAuth (Google Sign-In)
└─ API Token (Bearer authentication)
    ↓
Authorization Checks
├─ login_required decorator
├─ current_user validation
├─ User ownership validation
└─ Admin-only route protection
    ↓
Input Validation
├─ WTForms validators
├─ Email verification requirement
├─ Terms acceptance requirement
└─ Deletion cooldown enforcement
    ↓
Data Protection
├─ SQL Injection Prevention (SQLAlchemy ORM)
├─ XSS Prevention (Bleach sanitization)
├─ Password Security (Werkzeug bcrypt)
├─ Todo Encryption (Fernet - optional)
└─ API Token Security (secrets.token_urlsafe)
    ↓
Session Security
├─ httponly cookies
├─ same-site cookies
├─ 2-hour timeout
└─ Force re-authentication after logout
    ↓
Response (Secure)
```

### Security Features Added in v2.0

**Data Encryption:**
- Optional Fernet symmetric encryption for todo data
- PBKDF2 key derivation from SECRET_KEY
- Protection from database administrator access

**Account Security:**
- Email verification requirement for registration
- 7-day deletion cooldown to prevent immediate re-registration
- OAuth and direct login blocked during cooldown
- Force account selection after OAuth logout

**API Security:**
- Bearer token authentication
- Token generation with cryptographically secure randomness
- API-specific unauthorized handlers (JSON responses)
- CSRF exemption for API endpoints only

**Additional Protections:**
- Open redirect vulnerability fixes
- Command injection prevention (subprocess security)
- Print statement removal (no info disclosure)
- Logging instead of print statements

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

```text
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

## Third-Party Libraries Architecture (Updated v2.0)

```bash
Flask Framework & Extensions
├─ Flask 2.3.2 (Web framework)
├─ Flask-SQLAlchemy (ORM)
├─ Flask-Migrate (Database migrations via Alembic)
├─ Flask-WTF (Form handling + CSRF protection)
├─ Flask-Login (Session management)
├─ Flask-Mail (Email delivery)
└─ Werkzeug (Security, ProxyFix middleware)

Security & Encryption
├─ cryptography (Fernet encryption, PBKDF2 key derivation)
├─ bleach (HTML sanitization, XSS prevention)
├─ oauthlib 2.1.0 (OAuth 2.0)
└─ requests (HTTP client for OAuth)

Database
├─ SQLAlchemy (ORM, multi-database support)
├─ mysqlclient (MySQL driver)
├─ psycopg2-binary (PostgreSQL driver)
└─ Alembic (Migration management)

Frontend Libraries
├─ Bootstrap 4.6 (Responsive CSS framework)
├─ SimpleMDE (Markdown editor)
├─ DataTables (Data table plugin)
├─ Flatpickr (Date/time picker)
├─ Chart.js (Donut charts for dashboard)
├─ moment.js (Date formatting)
├─ jQuery 3.x (DOM manipulation - being phased out)
└─ marked.js (Markdown rendering)

Email & Communication
├─ smtplib (SMTP email delivery)
├─ email.mime (Email formatting)
└─ requests (External API calls)

Utilities
├─ Markdown (Markdown parsing)
├─ python-dotenv (Environment variable management)
├─ gunicorn (WSGI production server)
└─ secrets (Cryptographically secure token generation)

PWA Support
├─ Service Worker (Offline caching)
├─ Web App Manifest (PWA metadata)
└─ Cache API (Asset caching)
```

### JavaScript Modernization (v1.6.0)

**jQuery to Vanilla JS Migration:**
- 50+ jQuery instances replaced
- Fetch API replaces $.post() calls
- Native event listeners replace jQuery handlers
- ~15% faster JavaScript execution
- ~90% fewer API requests (quote fetching optimized)

**Intentional jQuery Retentions:**
- DataTables plugin (complex widget)
- SimpleMDE editor (dependency requirement)
- Bootstrap 4 framework (framework-level usage)

## Deployment Architecture Options

### Option 1: Standalone Server

```text
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

```text
Internet
    ↓
Nginx
    ↓
Docker Container (Flask + Gunicorn)
    ↓
External Database
```

### Option 3: Scalable

```text
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
