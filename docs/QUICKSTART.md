# Quick Reference Guide

## Getting Started Quickly

### First-Time Setup (5 minutes)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .flaskenv.example .flaskenv

# 4. Initialize database
flask db upgrade

# 5. Run application
flask run
```

**Access:** [http://localhost:5000](http://localhost:5000)  
*The application runs on port 5000 by default. Configure the PORT variable in `.flaskenv` to change it.*

---

## Common Commands

### Flask Commands

```bash
# Run development server
flask run

# Create database migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Show migration history
flask db history

# Generate secure salt
python3 -c "from app.config import generate_salt; print(generate_salt())"
```

### Database Commands

```bash
# Access SQLite database
sqlite3 instance/mysandbox.db

# Access MySQL database
mysql -u mysandbox -p -h localhost mysandbox

# Access PostgreSQL database
psql -U mysandbox -h localhost mysandbox
```

### Gunicorn Commands

```bash
# Run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 mysandbox:app

# Run with worker auto-reload
gunicorn -w 4 -b 0.0.0.0:5000 --reload mysandbox:app

# Run with access logging
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - mysandbox:app
```

---

## File Locations

| File | Purpose | Edit? |
|------|---------|-------|
| `app/config.py` | Configuration | ⚠️ Change before production |
| `.flaskenv` | Environment variables | ✏️ Edit for your environment |
| `app/models.py` | Database models | 📖 Reference |
| `app/routes.py` | Application endpoints | 📖 Reference |
| `app/forms.py` | Form validation | 📖 Reference |
| `app/templates/` | HTML templates | ✏️ Customize design |
| `instance/config.py` | Runtime config (optional) | ✏️ Instance-specific settings |

---

## API Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/login` | ❌ | User login |
| GET | `/logout` | ✅ | User logout |
| GET | `/todo` | ✅ | View today's todos |
| GET | `/<id>/list` | ✅ | View todos by date |
| POST | `/add` | ✅ | Create/update todo |
| POST | `/<id>/<todo_id>/done` | ✅ | Mark todo done |
| POST | `/<todo_id>/delete` | ✅ | Delete todo |
| GET/POST | `/account` | ✅ | Account settings |
| GET/POST | `/security` | ✅ | Change password |

---

## Database Models Quick Reference

### User

- Stores login credentials
- Key method: `set_password()`, `check_password()`
- One user has many todos

### Todo

- Stores task information
- Key method: `getList(type, start, end)`
- Has many status changes (via Tracker)

### Status

- Predefined status types (new, done, failed, re-assign)
- Key method: `seed()` - initializes defaults

### Tracker

- Tracks status history of todos
- Key method: `add()` - records status change

---

## Environment Variables

### Required

```bash
FLASK_APP=mysandbox.py
DATABASE_DEFAULT=mysql   # or sqlite (default), postgres
```

### Optional

```bash
FLASK_ENV=development     # or production
FLASK_DEBUG=1            # Enable debug mode
BIND_ADDRESS=127.0.0.1   # Server bind address
PORT=9191                # Server port
```

### MySQL/PostgreSQL Configuration

```bash
# Only required if DATABASE_DEFAULT is mysql or postgres
DB_URL=localhost         # Database host/IP
DB_USER=username         # Database user
DB_PASSWORD=password     # Database password (or use DB_PW)
DB_NAME=mysandbox        # Database name
```

**Note:** When using SQLite, `instance/` folder is created automatically. When using MySQL/PostgreSQL, `instance/` is not needed.

---

## Configuration Quick Reference

| Setting | File | Default | Notes |
|---------|------|---------|-------|
| SECRET_KEY | app/config.py | 'you-will-never-guess' | Change for production |
| SALT | app/config.py | (hardcoded) | Change for production |
| Session Timeout | app/**init__.py | 120 minutes | User logged out after timeout |
| Database Name | app/config.py | mysandbox.db | SQLite database filename |
| Database Default | app/config.py | sqlite | Which database to use |

---

## Debugging Tips

### Enable Debug Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Check Application Health

```bash
# View logs
tail -f /var/log/syslog | grep mysandbox

# Check response
curl http://127.0.0.1:9191/

# Database connectivity
flask shell
>>> from app import db
>>> db.session.execute('SELECT 1')
```

### Common Issues

#### "No module named 'app'"

- Ensure virtual environment is activated
- Check you're in correct directory

#### "Database locked"

- Close other database connections
- Check SQLite WAL files

#### "Port 9191 already in use"

- Change PORT in .flaskenv
- Or kill process: `lsof -i :9191 | kill -9 <PID>`

#### "CSRF validation failed"

- Ensure form includes `{{ csrf_token() }}`
- Check session is active

---

## Development Workflow

### Create Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes to models/routes/templates

# 3. Test locally
flask run

# 4. Commit changes
git add .
git commit -m "Add new feature"

# 5. Push and create PR
git push origin feature/new-feature
```

### Database Changes

```bash
# 1. Modify model in app/models.py

# 2. Create migration
flask db migrate -m "Add new field"

# 3. Review migration in migrations/versions/

# 4. Apply migration
flask db upgrade

# 5. Test thoroughly

# 6. Commit migration file
git add migrations/
git commit -m "Add migration"
```

---

## Form Usage

### Creating a Form

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class MyForm(FlaskForm):
    field_name = StringField('Label', validators=[validators.DataRequired()])
```

### Using in Template

```html
<form method="post">
    {{ form.hidden_tag() }}
    {{ form.field_name.label }}
    {{ form.field_name() }}
    {% if form.field_name.errors %}
        <ul>
        {% for error in form.field_name.errors %}
            <li>{{ error }}</li>
        {% endfor %}
        </ul>
    {% endif %}
    {{ form.submit() }}
</form>
```

---

## Template Tags & Filters

### Jinja2 Common Tags

```html
<!-- Conditionals -->
{% if condition %}...{% endif %}
{% if x else y %}...{% endif %}

<!-- Loops -->
{% for item in items %}
    {{ item }}
{% endfor %}

<!-- Inherited templates -->
{% extends "base.html" %}
{% block content %}...{% endblock %}
```

### Common Filters

```html
{{ text|upper }}          <!-- Uppercase -->
{{ text|lower }}          <!-- Lowercase -->
{{ text|title }}          <!-- Title case -->
{{ items|length }}        <!-- Length -->
{{ items|join(', ') }}    <!-- Join -->
{{ date|strftime('%Y-%m-%d') }}  <!-- Format date -->
```

---

## Testing Checklist

### Authentication

- [ ] Login with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] Session timeout works

### Todo Operations

- [ ] Create new todo
- [ ] Edit existing todo
- [ ] Mark todo as done
- [ ] Delete todo
- [ ] View today's todos
- [ ] View tomorrow's todos
- [ ] Markdown renders correctly

### Account Management

- [ ] Update username
- [ ] Update email
- [ ] Change password
- [ ] Old password validation works
- [ ] Password confirmation matches

---

## Performance Tips

1. **Limit Query Results**
   - Add pagination to large lists
   - Use `.limit()` on queries

2. **Cache Results**
   - Cache status types (rarely change)
   - Cache user data after login

3. **Database Optimization**
   - Add indexes on frequently searched columns
   - Use JOIN instead of N+1 queries

4. **Frontend Optimization**
   - Compress static files
   - Use CDN for assets
   - Minimize CSS/JavaScript

5. **Server Optimization**
   - Use production WSGI server (Gunicorn)
   - Increase worker processes
   - Use database connection pooling

---

## Security Checklist

- [ ] Change SECRET_KEY and SALT before production
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Disable debug mode in production
- [ ] Validate all user input
- [ ] Sanitize HTML output
- [ ] Use parameterized SQL queries
- [ ] Hash passwords (already done with Werkzeug)
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs

---

## Resource Links

### Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WTForms Documentation](https://wtforms.readthedocs.io/)

### Related Files in This Project

- Setup Guide: [SETUP.md](SETUP.md)
- API Reference: [API.md](API.md)
- Database Models: [MODELS.md](MODELS.md)
- Code Review: [CODE_REVIEW.md](CODE_REVIEW.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Quick Fixes

### Add New Model

1. Define in `app/models.py`
2. Run `flask db migrate -m "Add model"`
3. Run `flask db upgrade`

### Add New Route

1. Add function to `app/routes.py`
2. Decorate with `@app.route()`
3. Create template if needed

### Add Form Validation

1. Add validator to form in `app/forms.py`
2. Add custom validation method if needed
3. Check errors in template

### Add Database Field

1. Add column to model
2. Run `flask db migrate`
3. Review migration file
4. Run `flask db upgrade`

---

## Where to Find Help

| Issue | Location |
|-------|----------|
| Setup problems | [SETUP.md](SETUP.md) |
| API documentation | [API.md](API.md) |
| Database questions | [MODELS.md](MODELS.md) |
| Code improvements | [CODE_REVIEW.md](CODE_REVIEW.md) |
| How it works | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Deployment | [DEPLOYMENT.md](DEPLOYMENT.md) |
| This quick ref | [QUICKSTART.md](QUICKSTART.md) |

---

## Recent Updates (November 2025)

✅ **Security Patches Applied:**

- Hardcoded secrets replaced with environment variables
- XSS vulnerability fixed (HTML sanitization with bleach)
- SQL injection risk mitigated (input validation added)
- Form validation for duplicate accounts enabled

✅ **Werkzeug Compatibility Fixed:**

- Flask-WTF upgraded to 1.2.2
- Flask-Login upgraded to 0.6.3
- All deprecated imports updated
- Database migrations now working (`flask db upgrade` runs successfully)

✅ **Database Configuration Optimized:**

- MySQL now configured as primary database (192.168.1.112)
- Instance folder no longer created when using external database
- Multi-database support working (sqlite/mysql/postgres)

**Last Updated:** November 2025  
**Version:** 1.1  
**Status:** Production-ready (pending admin password change and database creation)
