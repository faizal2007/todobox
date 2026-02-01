# TodoBox

A Flask-based personal task management application with wisdom quotes, user authentication, and multi-database support.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment variables
cp .flaskenv.example .flaskenv

# 3. Create database and run migrations
flask db upgrade

# 4. Run the application
flask run
```

Visit `http://localhost:5000` in your browser.

## Key Features

### Core Functionality
- 📝 **Todo Management** - Create, organize, and track tasks with responsive grid layout
- ✅ **Simple & Advanced Modes** - Quick checklists or rich markdown content with on-the-fly conversion
- 🕐 **KIV Status** - Keep tasks in view with dedicated KIV (Keep In View) tab for tasks on hold
- 📋 **Status Tracking** - Track todo lifecycle: new, done, failed, re-assign with complete history

### User Experience
- 💡 **Wisdom Quotes** - Daily inspiration from ZenQuotes API with local fallback
- 🎨 **Modern UI** - Bootstrap 4 responsive design with grid layout and multiple themes
- 📱 **PWA Support** - Install as a Progressive Web App on mobile and desktop devices
- 📊 **Dashboard Analytics** - Donut charts grouped by time periods (today, weekly, monthly, yearly)
- 🏆 **Achievements Page** - View completed todos with infinite scroll and detailed completion stats

### Authentication & Security
- 👤 **User Authentication** - Email/password registration with verification and Google OAuth sign-in
- 🔒 **Secure** - Password hashing, CSRF protection, XSS prevention, security headers
- 🔐 **Data Encryption** - Optional Fernet encryption for todo data (protects from DB admins)
- 📧 **Email Verification** - Required for registration with 24-hour token expiration
- 📜 **Terms Management** - Versioned terms and disclaimer with admin control

### Collaboration Features
- 🤝 **Todo Sharing** - Share todos with other Gmail users (email-based invitations)
- 🔗 **Share Invitations** - Token-based approval system with 7-day expiration
- 👥 **Shared View** - Access todos shared by others in dedicated view

### Smart Features
- ⏰ **Smart Reminders** - Set reminders with automatic timezone detection and auto-close after 3 notifications
- 🌍 **Timezone Support** - Automatic IP-based timezone detection with 43+ timezone options
- 🔄 **Auto-Close Reminders** - Prevent reminder fatigue with auto-close after 3 notifications in 30 minutes

### API & Integration
- 🔑 **API Access** - RESTful API with Bearer token authentication for external integrations
- 🛠️ **API Token Management** - Generate, regenerate, and revoke API tokens via web interface

### Database & Deployment
- 💾 **Flexible Storage** - Support for SQLite, MySQL, and PostgreSQL
- 🧂 **Salt Generator** - Secure password hashing with cryptographically strong salts
- 🚀 **Ready to Deploy** - Production-ready with unified configuration
- ⚙️ **Admin Panel** - User management, terms management, blocked accounts control

### Account Management
- 🗑️ **Secure Deletion** - Email-verified account deletion with 7-day re-registration cooldown
- 🚫 **Deletion Cooldown** - Prevents immediate re-registration (both OAuth and direct login)

## Technology Stack

- **Framework:** Flask 2.3.2
- **Database:** SQLAlchemy with SQLite/MySQL/PostgreSQL support (9 models)
- **Authentication:** Flask-Login with Google OAuth 2.0 and email verification
- **Forms:** Flask-WTF with CSRF protection
- **Security:** Bleach for XSS prevention, Werkzeug password hashing, Fernet encryption (optional)
- **Email:** SMTP with 14+ anti-spam headers for deliverability
- **API:** RESTful API with Bearer token authentication
- **Frontend:** Bootstrap 4, vanilla JavaScript (jQuery being phased out), Jinja2 templates
- **PWA:** Service Worker v3, Web App Manifest, offline caching
- **Python:** 3.10+

**Status:** ✅ **Production Ready** (January 2026 - v2.0)

## Common Commands

```bash
# Development
flask run                    # Start dev server
flask shell                  # Flask interactive shell
flask db upgrade            # Run migrations

# Database
python3 -c "from app.config import generate_salt; print(generate_salt())"  # Generate secure salt

# Production
gunicorn -w 4 todobox:app  # Start with Gunicorn
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### Quick Start

- **[docs/README.md](docs/README.md)** - Documentation navigation and quick links
- **[docs/SETUP.md](docs/SETUP.md)** - Complete installation and configuration guide
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference with commands and API examples
- **[docs/USER_CREATION.md](docs/USER_CREATION.md)** - First-time user setup and management

### Core Documentation

- **[docs/API.md](docs/API.md)** - Full API reference with all endpoints and parameters
- **[docs/MODELS.md](docs/MODELS.md)** - Database schema and model documentation
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[docs/OVERVIEW.md](docs/OVERVIEW.md)** - Project overview, features, and architecture

### Operations & Security

- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment options and maintenance guide
- **[docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)** - Production deployment checklist
- **[docs/SECURITY_PATCHES.md](docs/SECURITY_PATCHES.md)** - Security improvements and patches applied
- **[docs/CODE_REVIEW.md](docs/CODE_REVIEW.md)** - Code review findings and best practices

### Features & Integrations

- **[docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)** - Google OAuth2 setup and configuration
- **[docs/KIV_STATUS.md](docs/KIV_STATUS.md)** - KIV (Keep In View) status feature documentation
- **[docs/AUTO_CLOSE_REMINDERS.md](docs/AUTO_CLOSE_REMINDERS.md)** - Auto-close reminder feature documentation
- **[docs/TIMEZONE_AUTO_DETECTION.md](docs/TIMEZONE_AUTO_DETECTION.md)** - Automatic timezone detection
- **[docs/TIMEZONE_INTEGRATION.md](docs/TIMEZONE_INTEGRATION.md)** - Timezone integration for reminders

### Sharing & Collaboration

- **[docs/SHARING.md](docs/SHARING.md)** - Todo sharing feature documentation (if exists)

### Code Quality & Performance

- **[docs/JAVASCRIPT_OPTIMIZATION.md](docs/JAVASCRIPT_OPTIMIZATION.md)** - JavaScript modernization (jQuery to vanilla JS)
- **[docs/JQUERY_MIGRATION_GUIDE.md](docs/JQUERY_MIGRATION_GUIDE.md)** - Developer guide for JavaScript patterns
- **[docs/AXE_LINTER_BEST_PRACTICES.md](docs/AXE_LINTER_BEST_PRACTICES.md)** - Accessibility guidelines

### Testing & Quality Gates

- **[docs/TEST_FILE_ORGANIZATION.md](docs/TEST_FILE_ORGANIZATION.md)** - Test file locations and organization guide
- **[docs/QUALITY_GATES_QUICK_REFERENCE.md](docs/QUALITY_GATES_QUICK_REFERENCE.md)** - Daily workflow with pre-commit/pre-push hooks
- **[docs/TESTING_AND_QUALITY_GATES.md](docs/TESTING_AND_QUALITY_GATES.md)** - Comprehensive testing system guide
- **[docs/QUALITY_GATE_SETUP.md](docs/QUALITY_GATE_SETUP.md)** - Setup and troubleshooting for quality gates
- **[docs/TESTING_STRATEGY_AND_CI_CD.md](docs/TESTING_STRATEGY_AND_CI_CD.md)** - Testing strategy and CI/CD integration
- **[docs/TESTING_SUMMARY.md](docs/TESTING_SUMMARY.md)** - Test coverage and results summary

### Migration Guides

- **[docs/README_MIGRATIONS.md](docs/README_MIGRATIONS.md)** - Database migration documentation
- **[docs/MIGRATION_FIX_GUIDE.md](docs/MIGRATION_FIX_GUIDE.md)** - Migration troubleshooting guide

### Complete Index

- **[docs/DOCUMENTATION_MASTER_INDEX.md](docs/DOCUMENTATION_MASTER_INDEX.md)** - Comprehensive documentation index with navigation paths and detailed sections

## Project Structure

```bash
todobox/
├── app/
│   ├── __init__.py         # Flask app factory (9KB)
│   ├── config.py           # Configuration & salt generator (3.5KB)
│   ├── models.py           # Database models - 9 models (26KB)
│   ├── routes.py           # Request handlers & API endpoints (155KB)
│   ├── forms.py            # WTForms definitions (5.5KB)
│   ├── utils.py            # Utility functions (4.9KB)
│   ├── oauth.py            # Google OAuth integration (5.6KB)
│   ├── email_service.py    # SMTP email delivery (10.4KB)
│   ├── encryption.py       # Data encryption service (4.7KB)
│   ├── verification.py     # Email verification tokens (2.2KB)
│   ├── reminder_service.py # Reminder system (7.6KB)
│   ├── geolocation.py      # IP-based timezone detection (4.3KB)
│   ├── timezone_utils.py   # Timezone utilities (2KB)
│   ├── cli.py              # Flask CLI commands (5.9KB)
│   ├── forms/              # Additional form modules
│   │   └── delete_account_form.py
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template with PWA manifest
│   │   ├── main.html       # Dashboard with donut charts
│   │   ├── list.html       # Todo list (responsive grid)
│   │   ├── undone.html     # Undone tasks + KIV tab
│   │   ├── achievements.html # Completed todos
│   │   ├── login.html      # Login with OAuth
│   │   ├── register.html   # Registration with email verification
│   │   ├── setup_wizard.html # 5-step setup guide
│   │   ├── sharing.html    # Todo sharing management
│   │   ├── shared_todos.html # View shared todos
│   │   ├── admin/          # Admin templates
│   │   └── ...
│   └── static/             # CSS, JS, images, fonts
│       ├── manifest.json   # PWA manifest
│       └── service-worker.js # PWA service worker (v3)
├── lib/
│   └── database.py         # Database connection utilities
├── migrations/             # 30+ database migration files
├── tests/                  # Test suite (227 tests, 80.6% passing)
├── docs/                   # 50+ documentation files
├── todobox.py              # App entry point
├── todomanage.py           # CLI management tool
├── .flaskenv               # Environment variables (create from example)
├── .flaskenv.example       # Configuration template
├── requirements.txt        # Python dependencies
├── CHANGELOG.md            # Recent changes and updates
├── SECURITY.md             # Security policy
├── LICENSE                 # MIT License
└── README.md               # This file
```

## API Endpoints

All API endpoints return **JSON** responses and require Bearer token authentication (except `/api/quote`).

### Authentication & Token Management

#### Generate API Token

```http
POST /api/auth/token
Authorization: Bearer <session-based or valid API token>
```

**Response (201 Created):**

```json
{
  "token": "9IXlqQjNYjk5xfhfmOKWGDWh6PTnY9g1",
  "message": "API token generated successfully. Keep this token secure!"
}
```

### Todo Management

#### List All Todos

```http
GET /api/todo
Authorization: Bearer YOUR_API_TOKEN
```

**Response (200 OK):**

```json
{
  "todos": [
    {
      "id": 1,
      "title": "Buy groceries",
      "details": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2025-11-26T06:49:12",
      "modified_at": "2025-11-26T06:49:12"
    }
  ]
}
```

#### Create New Todo

```http
POST /api/todo
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
  "title": "New Task",
  "details": "Optional task details (supports Markdown)"
}
```

**Response (201 Created):**

```json
{
  "id": 25,
  "title": "New Task",
  "details": "Optional task details",
  "status": "pending",
  "created_at": "2025-11-26T06:49:12",
  "modified_at": "2025-11-26T06:49:12"
}
```

#### Update Todo

```http
PUT /api/todo/<id>
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
  "title": "Updated title",
  "details": "Updated details",
  "status": "done"
}
```

**Response (200 OK):**

```json
{
  "id": 25,
  "title": "Updated title",
  "details": "Updated details",
  "status": "done",
  "created_at": "2025-11-26T06:49:12",
  "modified_at": "2025-11-26T07:15:33"
}
```

#### Delete Todo

```http
DELETE /api/todo/<id>
Authorization: Bearer YOUR_API_TOKEN
```

**Response (200 OK):**

```json
{
  "message": "Todo deleted successfully"
}
```

### Wisdom Quotes

#### Get Random Quote

```http
GET /api/quote
```

**Response (200 OK):**

```json
{
  "quote": "Stay focused"
}
```

### Web Interface Routes

- `GET /settings` - Settings page (password change and API token management)
- `GET /account` - Account information management
- `GET /dashboard` - Dashboard with statistics
- `GET /list/<date>` - Todo list for specific date (today/tomorrow)

## Configuration

Copy `.flaskenv.example` to `.flaskenv` and configure:

```bash
# Flask Settings
FLASK_ENV=development
FLASK_APP=todobox.py
SECRET_KEY=your-secret-key-here
SALT=your-salt-here

# Database (choose one)
DATABASE_DEFAULT=sqlite
# DATABASE_DEFAULT=mysql
# DATABASE_DEFAULT=postgres

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:5000/auth/callback/google
```

## Database Setup

### SQLite (Default)

Auto-created on first run - no additional setup needed.

### MySQL

```bash
CREATE DATABASE todobox_db;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON todobox_db.* TO 'user'@'localhost';
```

### PostgreSQL

Set `DATABASE_DEFAULT=postgres` in `.flaskenv` and ensure PostgreSQL is installed.

## API Token Management

Users can generate and manage API tokens through the web interface:

1. **Access Settings**: Navigate to Profile → Settings
2. **Generate Token**: Click "Generate API Token" to create a new token
3. **Copy Token**: Use the copy button to copy your token securely
4. **Regenerate**: Generate a new token (old token becomes invalid)
5. **Revoke**: Permanently remove API access

**Security Notes:**

- Keep your API token secure and never share it publicly
- Tokens provide full access to your todo data
- Regenerate tokens regularly for security
- Revoke tokens immediately if compromised

**Example API Usage:**

```bash
# Get all todos
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:5000/api/todo

# Create a new todo
curl -X POST -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "details": "Task details"}' \
  http://localhost:5000/api/todo
```

## Recent Updates

See [CHANGELOG.md](CHANGELOG.md) for all recent changes including:

- **Latest Fixes** (December 2025):
  - Fixed Mark as KIV button on undone page
  - Fixed dashboard date display issues
  - Created comprehensive test suite against real MySQL database
  - Reorganized documentation structure
  
- **Previous Updates**:
  - KIV (Keep In View) status feature with dedicated tab
  - Separated KIV table from status tracking
  - Fixed route redirect logic
  - Enhanced test suite accuracy
  
- **Security & Performance**:
  - XSS prevention and security headers
  - JavaScript optimization (jQuery to vanilla JS)
  - Input validation and sanitization
  - Auto-generated secure SECRET_KEY

For detailed changelog, see [CHANGELOG.md](CHANGELOG.md)

## Quick Tips

- **Generate a new salt:** `python3 -c "from app.config import generate_salt; print(generate_salt())"`
- **Access setup wizard:** Navigate to `/setup` after starting the app
- **View todos:** All todos displayed in responsive 3-4 column grid
- **Get daily quote:** Quote shown in header and `/api/quote` endpoint

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial use, as long as you include the original copyright notice and license terms.
