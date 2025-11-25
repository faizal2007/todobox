# Setup & Installation Guide

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Virtual environment tools
- MySQL development libraries (if using MySQL)

## Getting Started

### 1. Install System Dependencies

For Debian/Ubuntu systems:

```bash
apt-get install python3-venv default-libmysqlclient-dev
```

For macOS:

```bash
brew install mysql-client
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example configuration:

```bash
cp .flaskenv.example .flaskenv
```

Edit `.flaskenv` with your settings:

```bash
# Required
FLASK_APP=mysandbox.py
FLASK_ENV=development
DATABASE_DEFAULT=mysql  # or sqlite (default), postgres

# Application settings
BIND_ADDRESS=127.0.0.1
PORT=9191

# For MySQL/PostgreSQL only
DB_URL=localhost
DB_USER=username
DB_PASSWORD=password    # or use DB_PW
DB_NAME=mysandbox
```

**Important:**

- Set `DATABASE_DEFAULT=mysql` to use external MySQL (no instance/ folder needed)
- Leave `DATABASE_DEFAULT` unset or use `sqlite` for development with SQLite database

### 5. Initialize Database

For first-time setup:

```bash
flask db upgrade
```

This creates the database schema and seeds default data (admin user and status types).

### 6. Run the Application

```bash
flask run
```

Or using the entry point:

```bash
python mysandbox.py
```

The application will be available at `http://127.0.0.1:9191`

## Database Configuration

### SQLite (Default)

No additional configuration needed. Database file will be created at:

```text
instance/mysandbox.db
```

### MySQL

1. Create database and user:

   ```sql
   CREATE DATABASE mysandbox;
   CREATE USER 'mysandbox'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON mysandbox.* TO 'mysandbox'@'localhost';
   FLUSH PRIVILEGES;
   ```

1. Configure `.flaskenv`:

   ```bash
   DATABASE_DEFAULT=mysql
   DB_URL=localhost
   DB_USER=mysandbox
   DB_PW=password
   DB_NAME=mysandbox
   ```

1. Initialize database:

   ```bash
   flask db upgrade
   ```

### PostgreSQL

1. Create database and user:

   ```sql
   CREATE USER mysandbox WITH PASSWORD 'password';
   CREATE DATABASE mysandbox OWNER mysandbox;
   ```

1. Configure `.flaskenv`:

   ```bash
   DATABASE_DEFAULT=postgres
   DB_URL=localhost
   DB_USER=mysandbox
   DB_PW=password
   DB_NAME=mysandbox
   ```

1. Initialize database:

   ```bash
   flask db upgrade
   ```

## Running in Production

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:9191 mysandbox:app
```

### Configuration Options

- `-w`: Number of worker processes (2-4 × CPU cores)
- `-b`: Bind address and port
- `--workers`: Alternative to `-w`
- `--timeout`: Worker timeout in seconds
- `--access-logfile`: Log file for access logs

### Environment Setup for Production

1. Set `FLASK_ENV=production` in `.flaskenv`
2. Use a strong `SECRET_KEY` in `app/config.py`
3. Set `DEBUG=False`
4. Use a production database (MySQL or PostgreSQL)
5. Configure HTTPS/SSL
6. Set up proper logging

## Development Configuration

For development, useful settings:

```bash
FLASK_ENV=development
FLASK_DEBUG=1
```

This enables:

- Auto-reloader on file changes
- Detailed error pages
- Debug toolbar integration

## Database Migrations

### Create New Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

### View Migration History

```bash
flask db history
```

## Troubleshooting

### "No such file or directory: instance/mysandbox.db"

The instance directory is only needed for SQLite. If using MySQL/PostgreSQL:

- Ensure `DATABASE_DEFAULT=mysql` (or postgres) is set in `.flaskenv`
- Create the database on your MySQL/PostgreSQL server first
- Then run `flask db upgrade`

For SQLite development:

```bash
mkdir instance
flask db upgrade
```

### Database Connection Error

Verify `.flaskenv` settings and database server is running:

```bash
# For MySQL
mysql -u mysandbox -p -h localhost mysandbox

# For PostgreSQL
psql -U mysandbox -h localhost mysandbox
```

### Module Import Errors

Ensure virtual environment is activated and dependencies installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

Change the port in `.flaskenv`:

```bash
PORT=9192
```

Or kill the process using the port:

```bash
lsof -i :9191
kill -9 <PID>
```

## Initial User Credentials

After setup, a default admin user is automatically created:

- **Username**: admin
- **Password**: admin1234

⚠️ **CRITICAL**: Change the admin password immediately after first login for security.

### Change Admin Password

1. Login with `admin / admin1234`
2. Go to `/security` or account settings
3. Change password to a strong value
4. Confirm change

### Alternative: Reset via Database

If you need to reset the admin password, you can modify it in the database:

```bash
# For SQLite
sqlite3 instance/mysandbox.db
SELECT * FROM "user" WHERE username='admin';

# To reset, delete the admin user and let the app recreate it
DELETE FROM "user" WHERE username='admin';
```

Then restart the application and re-run `flask db upgrade` to recreate the default user.

## Verification

After setup, verify the installation:

1. Run migrations: `flask db upgrade` ✅ (Confirmed working - November 2025)
2. Start the application: `flask run`
3. Open browser to `http://127.0.0.1:9191`
4. Login with admin/admin1234
5. Create a test todo item
6. Verify functionality (add, mark done, delete)
7. **IMPORTANT**: Change admin password via `/security`

✅ All systems operational if you can create, view, and modify todo items without errors.

### Verification Status (as of November 2025)

- ✅ App imports successfully
- ✅ Flask database migrations work
- ✅ MySQL connection established (when configured)
- ✅ All security patches applied
- ✅ Werkzeug 3.0.6 compatibility verified
- ⏳ MySQL database 'shimasu_db' needs to be created on database server
- ⏳ Admin password needs to be changed after first login
