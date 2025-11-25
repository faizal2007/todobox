# MySandbox

A Flask-based personal task management and note-taking application with multi-database support.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment variables (copy template)
cp .flaskenv.example .flaskenv

# 3. Create database and run migrations
flask db upgrade

# 4. Create first admin user
python create_user.py

# 5. Run the application
flask run
```

Visit `http://localhost:5000` in your browser.

## Key Features

- 📝 **Todo Management** - Create, organize, and track tasks
- 📚 **Note Taking** - Rich text notes with markdown support
- 👤 **Multi-User** - User authentication and account management
- 🔒 **Secure** - Password hashing, CSRF protection, XSS prevention
- 💾 **Flexible Storage** - Support for SQLite, MySQL, and PostgreSQL
- 🚀 **Production Ready** - Gunicorn and Nginx deployment guides

## Technology Stack

- **Framework:** Flask 2.3.2
- **Database:** SQLAlchemy 1.4.17 (SQLite, MySQL, PostgreSQL)
- **Authentication:** Flask-Login 0.6.3 ✅ (corrected)
- **Forms:** Flask-WTF 1.2.2
- **Security:** Bleach 6.3.0, Werkzeug 3.0.6
- **Python:** 3.10.12+ (all 27 packages verified compatible)

**Status:** ✅ **Production Ready** (November 25, 2025)

## Documentation

Complete documentation is available in the `/docs` folder:

- **[📖 Documentation Index](docs/DOCUMENTATION_MASTER_INDEX.md)** - Full navigation guide
- **[🚀 Quick Start](docs/QUICKSTART.md)** - Quick reference guide
- **[⚙️ Setup Guide](docs/SETUP.md)** - Detailed installation
- **[🔌 API Reference](docs/API.md)** - Complete API documentation
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System design
- **[📦 Models](docs/MODELS.md)** - Database schema
- **[👥 User Management](docs/USER_CREATION.md)** - User creation & CLI commands
- **[🚢 Deployment](docs/DEPLOYMENT.md)** - Production setup
- **[📋 Code Review](docs/CODE_REVIEW.md)** - Code quality analysis

## Common Commands

```bash
# Development
flask run                    # Start dev server
flask shell                  # Flask shell
flask db upgrade            # Run migrations

# User Management
python create_user.py       # Interactive user creation
flask create-user           # CLI user creation
flask list-users            # Show all users
flask reset-password        # Change user password
flask delete-user           # Remove user

# Production
gunicorn -w 4 mysandbox:app  # Start with Gunicorn
```

## Project Structure

```text
mysandbox/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── routes.py           # Request handlers
│   ├── forms.py            # WTForms definitions
│   ├── utils.py            # Utility functions
│   ├── cli.py              # Flask CLI commands
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── lib/
│   └── database.py         # Database connection
├── migrations/             # Database migrations
├── create_user.py          # User creation script
├── mysandbox.py            # App entry point
├── .flaskenv               # Environment variables
├── requirements.txt        # Python dependencies
└── docs/                   # Complete documentation
```

## Database Setup

### MySQL

```bash
# Create database and user on MySQL server
CREATE DATABASE shimasu_db;
CREATE USER 'freakie'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON shimasu_db.* TO 'freakie'@'localhost';
```

### PostgreSQL

Set `DATABASE_DEFAULT=postgres` in `.flaskenv`

### SQLite (Default)

No setup needed - database is auto-created

## Configuration

Environment variables in `.flaskenv`:

```bash
FLASK_ENV=development
FLASK_APP=mysandbox.py
DATABASE_DEFAULT=mysql          # sqlite, mysql, or postgres
DB_URL=localhost:3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=shimasu_db
SECRET_KEY=your_secret_key
```

## Security

- ✅ Environment variables for secrets (no hardcoded credentials)
- ✅ XSS protection with HTML sanitization
- ✅ SQL injection prevention with parameterized queries
- ✅ CSRF protection with Flask-WTF
- ✅ Password hashing with werkzeug security
- ✅ Duplicate user prevention
- ✅ Account security features

## Troubleshooting

Having issues? Check the documentation:

- **Setup problems?** → [SETUP.md](docs/SETUP.md)
- **API issues?** → [API.md](docs/API.md)
- **Deployment?** → [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **User management?** → [USER_CREATION.md](docs/USER_CREATION.md)
- **Code quality?** → [CODE_REVIEW.md](docs/CODE_REVIEW.md)

## Contributing

When making changes:

1. Follow the code review guidelines in [CODE_REVIEW.md](docs/CODE_REVIEW.md)
2. Test thoroughly with all supported databases
3. Update documentation as needed
4. Ensure security best practices are followed

## License

This project is provided as-is for educational and personal use.

## Support

Refer to the comprehensive documentation in the `/docs` folder for detailed help and guides.

---

**Need more information?** Start with [📖 Documentation Index](docs/DOCUMENTATION_MASTER_INDEX.md) in the docs folder.
