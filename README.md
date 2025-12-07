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
```yaml

Visit `http://localhost:5000` in your browser.

## Key Features

- 📝 **Todo Management** - Create, organize, and track tasks with responsive grid layout
- 🕐 **KIV Status** - Keep tasks in view with dedicated KIV (Keep In View) status for tasks on hold
- 💡 **Wisdom Quotes** - Daily inspiration from ZenQuotes API with local fallback
- 👤 **User Authentication** - Email/password and Google OAuth sign-in
- 🎨 **Modern UI** - Bootstrap 4 responsive design with multiple themes
- 🔒 **Secure** - Password hashing, CSRF protection, XSS prevention
- 💾 **Flexible Storage** - Support for SQLite, MySQL, and PostgreSQL
- 🧂 **Salt Generator** - Secure password hashing with cryptographically strong salts
- 🚀 **Ready to Deploy** - Production-ready with unified configuration
- 🔑 **API Access** - RESTful API with token-based authentication for external integrations
- ⏰ **Smart Reminders** - Set reminders with automatic timezone detection and auto-close after 3 notifications
- 🌍 **Timezone Support** - Automatic timezone detection based on IP geolocation with 43+ timezone options
- 📱 **PWA Support** - Install as a Progressive Web App on mobile and desktop devices
- 📊 **Dashboard Analytics** - Track tasks with donut charts grouped by time periods (today, weekly, monthly, yearly)

## Technology Stack

- **Framework:** Flask 2.3.2
- **Database:** SQLAlchemy with SQLite/MySQL/PostgreSQL support
- **Authentication:** Flask-Login with Google OAuth
- **Forms:** Flask-WTF with CSRF protection
- **Security:** Bleach for XSS prevention, Werkzeug password hashing
- **API:** Server-side quote fetching (eliminates CORS errors)
- **Frontend:** Bootstrap 4, Jinja2 templates
- **Python:** 3.10+

**Status:** ✅ **Production Ready** (December 2025)

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
```python

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### Getting Started

- **[README.md](docs/README.md)** - Documentation index and quick links
- **[SETUP.md](docs/SETUP.md)** - Complete installation and configuration guide
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference with commands and API examples
- **[USER_CREATION.md](docs/USER_CREATION.md)** - First-time user setup and management

### Reference Documentation

- **[API.md](docs/API.md)** - Full API reference with all endpoints and parameters
- **[MODELS.md](docs/MODELS.md)** - Database schema and model documentation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[OVERVIEW.md](docs/OVERVIEW.md)** - Project overview, features, and architecture

### Operations & Security

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment options and maintenance guide
- **[DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)** - Production deployment checklist
- **[SECURITY_PATCHES.md](docs/SECURITY_PATCHES.md)** - Security improvements and patches applied
- **[CODE_REVIEW.md](docs/CODE_REVIEW.md)** - Code review findings and best practices

### OAuth & Authentication

- **[OAUTH_SETUP.md](docs/OAUTH_SETUP.md)** - Google OAuth2 setup and configuration

### Code Quality & Performance

- **[JAVASCRIPT_OPTIMIZATION.md](docs/JAVASCRIPT_OPTIMIZATION.md)** - JavaScript modernization (jQuery to vanilla JS)
- **[JQUERY_MIGRATION_GUIDE.md](docs/JQUERY_MIGRATION_GUIDE.md)** - Developer guide for JavaScript patterns
- **[AXE_LINTER_BEST_PRACTICES.md](docs/AXE_LINTER_BEST_PRACTICES.md)** - Accessibility guidelines

### Features & Integrations

- **[KIV_STATUS.md](docs/KIV_STATUS.md)** - KIV (Keep In View) status feature documentation
- **[AUTO_CLOSE_REMINDERS.md](docs/AUTO_CLOSE_REMINDERS.md)** - Auto-close reminder feature documentation
- **[TIMEZONE_AUTO_DETECTION.md](docs/TIMEZONE_AUTO_DETECTION.md)** - Automatic timezone detection
- **[TIMEZONE_INTEGRATION.md](docs/TIMEZONE_INTEGRATION.md)** - Timezone integration for reminders

### Migration Guides

- **[README_MIGRATIONS.md](docs/README_MIGRATIONS.md)** - Database migration documentation
- **[MIGRATION_FIX_GUIDE.md](docs/MIGRATION_FIX_GUIDE.md)** - Migration troubleshooting guide

## Project Structure

```bash
todobox/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration & salt generator
│   ├── models.py           # Database models (Todo, User)
│   ├── routes.py           # Request handlers & API endpoints
│   ├── forms.py            # WTForms definitions
│   ├── utils.py            # Utility functions
│   ├── oauth.py            # Google OAuth integration
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template
│   │   ├── main.html       # Main app template
│   │   ├── list.html       # Todo list (responsive grid)
│   │   ├── login.html      # Login page
│   │   ├── setup_wizard.html # 5-step setup guide
│   │   └── ...
│   └── static/             # CSS, JS, images, fonts
├── lib/
│   └── database.py         # Database connection utilities
├── migrations/             # Database migration files
├── todobox.py            # App entry point
├── .flaskenv               # Environment variables (create from .flaskenv.example)
├── .flaskenv.example       # Configuration template
├── requirements.txt        # Python dependencies
├── CHANGELOG.md            # Recent changes and updates
└── docs/                   # Documentation (if available)
```python

## API Endpoints

All API endpoints return **JSON** responses and require Bearer token authentication (except `/api/quote`).

### Authentication & Token Management

#### Generate API Token

```http
POST /api/auth/token
Authorization: Bearer <session-based or valid API token>
```python

**Response (201 Created):**

```json
{
  "token": "9IXlqQjNYjk5xfhfmOKWGDWh6PTnY9g1",
  "message": "API token generated successfully. Keep this token secure!"
}
```yaml

### Todo Management

#### List All Todos

```http
GET /api/todo
Authorization: Bearer YOUR_API_TOKEN
```json

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
```yaml

#### Create New Todo

```http
POST /api/todo
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
  "title": "New Task",
  "details": "Optional task details (supports Markdown)"
}
```yaml

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
```sql

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
```sql

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
```yaml

#### Delete Todo

```http
DELETE /api/todo/<id>
Authorization: Bearer YOUR_API_TOKEN
```yaml

**Response (200 OK):**

```json
{
  "message": "Todo deleted successfully"
}
```json

### Wisdom Quotes

#### Get Random Quote

```http
GET /api/quote
```json

**Response (200 OK):**

```json
{
  "quote": "Stay focused"
}
```yaml

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
```python

## Database Setup

### SQLite (Default)

Auto-created on first run - no additional setup needed.

### MySQL

```bash
CREATE DATABASE todobox_db;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON todobox_db.* TO 'user'@'localhost';
```sql

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
```yaml

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
