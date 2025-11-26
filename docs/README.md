# TodoBox Documentation

This documentation provides comprehensive information about the TodoBox
Flask application - a todo management system with user authentication
and task tracking capabilities.

## Contents

- **[OVERVIEW.md](OVERVIEW.md)** - Project overview, architecture, and feature description
- **[SETUP.md](SETUP.md)** - Installation, configuration, and deployment instructions
- **[API.md](API.md)** - Complete API reference and endpoint documentation
- **[MODELS.md](MODELS.md)** - Database models and data structure
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code review findings, best practices, and recommendations
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Project structure and architectural patterns
- **[USER_CREATION.md](USER_CREATION.md)** - User creation and CLI commands
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and maintenance guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[OAUTH_SETUP.md](OAUTH_SETUP.md)** - Google OAuth2 setup guide

## Quick Links

- [Getting Started](SETUP.md#getting-started)
- [Database Configuration](SETUP.md#database-configuration)
- [Available Routes](API.md)
- [Database Schema](MODELS.md#database-schema)
- [Identified Issues](CODE_REVIEW.md#identified-issues)

## Technology Stack

- **Framework**: Flask 2.3.2
- **Database ORM**: SQLAlchemy 1.4.17
- **Authentication**: Flask-Login 0.6.3
- **Database Migrations**: Flask-Migrate 4.1.0 (Alembic 1.13.2)
- **Form Validation**: WTForms 3.2.1
- **Security**: Werkzeug 3.0.6, Bleach 6.3.0
- **Server**: Gunicorn 23.0.0

## Application Features

- User authentication and login management
- Google OAuth2 authentication support
- Create, read, and manage todo items
- Mark tasks as complete
- Task scheduling (today/tomorrow/custom date)
- Change password and account management
- Markdown support for task descriptions
- HTML sanitization for XSS prevention
- Session management with timeout
- CSRF protection
