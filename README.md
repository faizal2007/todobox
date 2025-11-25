# MySandbox

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

- 📝 **Todo Management** - Create, organize, and track tasks with responsive grid layout
- 💡 **Wisdom Quotes** - Daily inspiration from ZenQuotes API with local fallback
- 👤 **User Authentication** - Email/password and Google OAuth sign-in
- 🎨 **Modern UI** - Bootstrap 4 responsive design with multiple themes
- 🔒 **Secure** - Password hashing, CSRF protection, XSS prevention
- 💾 **Flexible Storage** - Support for SQLite, MySQL, and PostgreSQL
- 🧂 **Salt Generator** - Secure password hashing with cryptographically strong salts
- 🚀 **Ready to Deploy** - Production-ready with unified configuration
- 🔑 **API Access** - RESTful API with token-based authentication for external integrations

## Technology Stack

- **Framework:** Flask 2.3.2
- **Database:** SQLAlchemy with SQLite/MySQL/PostgreSQL support
- **Authentication:** Flask-Login with Google OAuth
- **Forms:** Flask-WTF with CSRF protection
- **Security:** Bleach for XSS prevention, Werkzeug password hashing
- **API:** Server-side quote fetching (eliminates CORS errors)
- **Frontend:** Bootstrap 4, Jinja2 templates
- **Python:** 3.10+

**Status:** ✅ **Production Ready** (November 26, 2025)

## Common Commands

```bash
# Development
flask run                    # Start dev server
flask shell                  # Flask interactive shell
flask db upgrade            # Run migrations

# Database
python3 -c "from app.config import generate_salt; print(generate_salt())"  # Generate secure salt

# Production
gunicorn -w 4 mysandbox:app  # Start with Gunicorn
```

## Project Structure

```bash
mysandbox/
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
├── mysandbox.py            # App entry point
├── .flaskenv               # Environment variables (create from .flaskenv.example)
├── .flaskenv.example       # Configuration template
├── requirements.txt        # Python dependencies
├── CHANGELOG.md            # Recent changes and updates
└── docs/                   # Documentation (if available)
```

## API Endpoints

### Authentication

- `POST /api/auth/token` - Generate API token (requires session auth)

### Todo Management

- `GET /api/todo` - Fetch all todos (requires API token)
- `POST /api/todo` - Create new todo (requires API token)
- `PUT /api/todo/<id>` - Update todo (requires API token)
- `DELETE /api/todo/<id>` - Delete todo (requires API token)

### Wisdom Quotes

- `GET /api/quote` - Fetch random wisdom quote (public)

### User Interface

- `GET /settings` - Settings page (password change and API token management)
- `GET /account` - Account information management
- `GET /setup` - Interactive setup wizard

## Configuration

Copy `.flaskenv.example` to `.flaskenv` and configure:

```bash
# Flask Settings
FLASK_ENV=development
FLASK_APP=mysandbox.py
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
CREATE DATABASE mysandbox_db;
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON mysandbox_db.* TO 'user'@'localhost';
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

- Wisdom quotes integration (ZenQuotes + local fallback)
- Salt generator function
- Todo grid layout reorganization
- Setup wizard implementation
- Configuration consolidation
- CORS fixes

## Quick Tips

- **Generate a new salt:** `python3 -c "from app.config import generate_salt; print(generate_salt())"`
- **Access setup wizard:** Navigate to `/setup` after starting the app
- **View todos:** All todos displayed in responsive 3-4 column grid
- **Get daily quote:** Quote shown in header and `/api/quote` endpoint

## License

This project is provided as-is for educational and personal use.
