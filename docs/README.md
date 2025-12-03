# TodoBox Documentation

This documentation provides comprehensive information about the TodoBox
Flask application - a todo management system with user authentication
and task tracking capabilities.

**Last Updated:** December 3, 2025

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
- **[SECURITY_FIX_PRINT_STATEMENTS.md](SECURITY_FIX_PRINT_STATEMENTS.md)** - Print statement security fixes
- **[AXE_LINTER_BEST_PRACTICES.md](AXE_LINTER_BEST_PRACTICES.md)** - Accessibility guidelines

### Testing Documentation

- **[TESTING_COMPLETE.md](TESTING_COMPLETE.md)** - Comprehensive testing documentation

### Feature Documentation

- **[AUTO_CLOSE_REMINDERS.md](AUTO_CLOSE_REMINDERS.md)** - Auto-close reminder feature guide
- **[REMINDER_FEATURE_FIX.md](REMINDER_FEATURE_FIX.md)** - Reminder 30-minute interval fix
- **[TIMEZONE_AUTO_DETECTION.md](TIMEZONE_AUTO_DETECTION.md)** - Timezone auto-detection feature
- **[TIMEZONE_INTEGRATION.md](TIMEZONE_INTEGRATION.md)** - Timezone integration documentation

### JavaScript/jQuery Modernization

- **[JAVASCRIPT_OPTIMIZATION.md](JAVASCRIPT_OPTIMIZATION.md)** - JavaScript modernization technical reference
- **[JAVASCRIPT_OPTIMIZATION_EXECUTIVE_SUMMARY.md](JAVASCRIPT_OPTIMIZATION_EXECUTIVE_SUMMARY.md)** - Executive summary
- **[JQUERY_MIGRATION_GUIDE.md](JQUERY_MIGRATION_GUIDE.md)** - Developer migration guide
- **[DEVELOPMENT_SESSION_DECEMBER_2025.md](DEVELOPMENT_SESSION_DECEMBER_2025.md)** - December 2025 development session

### Migration Guides

- **[README_MIGRATIONS.md](README_MIGRATIONS.md)** - Migration quick reference
- **[MIGRATION_FIX_GUIDE.md](MIGRATION_FIX_GUIDE.md)** - Migration troubleshooting
- **[MIGRATION_FIX_SUMMARY.md](MIGRATION_FIX_SUMMARY.md)** - Migration fix summary
- **[MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md)** - Migration chain analysis
- **[MIGRATION_TEST_RESULTS.md](MIGRATION_TEST_RESULTS.md)** - Migration test results

### Technical Notes

- **[WERKZEUG_FIX.md](WERKZEUG_FIX.md)** - Werkzeug 3.0 compatibility fixes
- **[PROGRESS_NOVEMBER_2025.md](PROGRESS_NOVEMBER_2025.md)** - November 2025 progress

### Documentation Index

- **[INDEX.md](INDEX.md)** - Documentation summary and navigation
- **[DOCUMENTATION_MASTER_INDEX.md](DOCUMENTATION_MASTER_INDEX.md)** - Complete index

## Documentation Statistics

- **Total Files:** 33 markdown files
- **Total Size:** ~592 KB
- **Code Examples:** 150+
- **Diagrams:** 15+
- **Tables:** 50+

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
- Mark tasks as complete
- Task scheduling (today/tomorrow/custom date)
- Dashboard with statistics
- Change password and account management
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
