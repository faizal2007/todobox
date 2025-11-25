# MySandbox Documentation

This documentation provides comprehensive information about the MySandbox Flask application - a todo management system with user authentication and task tracking capabilities.

## Contents

- **[OVERVIEW.md](OVERVIEW.md)** - Project overview, architecture, and feature description
- **[SETUP.md](SETUP.md)** - Installation, configuration, and deployment instructions
- **[API.md](API.md)** - Complete API reference and endpoint documentation
- **[MODELS.md](MODELS.md)** - Database models and data structure
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code review findings, best practices, and recommendations
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Project structure and architectural patterns

## Quick Links

- [Getting Started](SETUP.md#getting-started)
- [Database Configuration](SETUP.md#database-configuration)
- [Available Routes](API.md)
- [Database Schema](MODELS.md#database-schema)
- [Identified Issues](CODE_REVIEW.md#identified-issues)

## Technology Stack

- **Framework**: Flask 2.3.2
- **Database ORM**: SQLAlchemy 1.4.17
- **Authentication**: Flask-Login 0.6.2
- **Database Migrations**: Alembic 1.6.5
- **Form Validation**: WTForms 2.3.3
- **Server**: Gunicorn 20.1.0

## Application Features

- User authentication and login management
- Create, read, and manage todo items
- Mark tasks as complete
- Task scheduling (today/tomorrow)
- Change password and account management
- Markdown support for task descriptions
- Session management with timeout
- CSRF protection
