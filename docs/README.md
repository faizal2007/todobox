# TodoBox Documentation

This documentation provides comprehensive information about the TodoBox
Flask application - a todo management system with user authentication
and task tracking capabilities.

**Last Updated:** December 7, 2025

## Contents

### Getting Started

- **[OVERVIEW.md](OVERVIEW.md)** - Project overview and feature description
- **[SETUP.md](SETUP.md)** - Installation and configuration guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[USER_CREATION.md](USER_CREATION.md)** - User creation and CLI commands

### Reference Documentation

- **[API.md](API.md)** - Complete API reference and endpoints
- **[MODELS.md](MODELS.md)** - Database models and data structure
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Project structure and patterns

### Operations & Deployment

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and maintenance guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Production deployment checklist
- **[OAUTH_SETUP.md](OAUTH_SETUP.md)** - Google OAuth2 setup guide

### Code Quality & Security

- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code review findings and recommendations
- **[SECURITY_PATCHES.md](SECURITY_PATCHES.md)** - Security improvements applied
- **[AXE_LINTER_BEST_PRACTICES.md](AXE_LINTER_BEST_PRACTICES.md)** - Accessibility guidelines

### Migration Guides

- **[README_MIGRATIONS.md](README_MIGRATIONS.md)** - Migration quick reference
- **[MIGRATION_FIX_GUIDE.md](MIGRATION_FIX_GUIDE.md)** - Migration troubleshooting

### Features & Integrations

- **[KIV_STATUS.md](KIV_STATUS.md)** - KIV (Keep In View) status feature
- **[AUTO_CLOSE_REMINDERS.md](AUTO_CLOSE_REMINDERS.md)** - Auto-close reminder feature documentation
- **[TIMEZONE_AUTO_DETECTION.md](TIMEZONE_AUTO_DETECTION.md)** - Automatic timezone detection
- **[TIMEZONE_INTEGRATION.md](TIMEZONE_INTEGRATION.md)** - Timezone integration for reminders

### Performance & Optimization

- **[JAVASCRIPT_OPTIMIZATION.md](JAVASCRIPT_OPTIMIZATION.md)** - JavaScript modernization details
- **[JQUERY_MIGRATION_GUIDE.md](JQUERY_MIGRATION_GUIDE.md)** - jQuery to vanilla JS patterns

### Documentation Index

- **[INDEX.md](INDEX.md)** - Documentation summary and navigation
- **[DOCUMENTATION_MASTER_INDEX.md](DOCUMENTATION_MASTER_INDEX.md)** - Complete index

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
- RESTful API with token-based authentication
- Create, read, and manage todo items
- Mark tasks as complete or KIV (Keep In View)
- Task scheduling (today/tomorrow/custom date)
- Dashboard with statistics and time-period grouping
- Change password and account management
- Smart reminders with auto-close functionality
- Automatic timezone detection
- PWA support for mobile and desktop
- Markdown support for task descriptions
- HTML sanitization for XSS prevention
- Session management with timeout
- CSRF protection

## Screenshots

Screenshots are available in the [screenshots](screenshots/) folder:

- `dashboard.png` - Dashboard overview
- `login.png` - Login page
- `save-todo.png` - Todo creation
- `delete-todo.png` - Todo deletion
