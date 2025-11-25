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
# For SQLite (default)
FLASK_APP=mysandbox.py
FLASK_ENV=development
BIND_ADDRESS=127.0.0.1
PORT=9191

# For MySQL/PostgreSQL
DATABASE_DEFAULT=mysql  # or postgres
DB_URL=localhost
DB_USER=username
DB_PW=password
DB_NAME=mysandbox
```

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

```
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

2. Configure `.flaskenv`:

```bash
DATABASE_DEFAULT=mysql
DB_URL=localhost
DB_USER=mysandbox
DB_PW=password
DB_NAME=mysandbox
```

3. Initialize database:

```bash
flask db upgrade
```

### PostgreSQL

1. Create database and user:

```sql
CREATE USER mysandbox WITH PASSWORD 'password';
CREATE DATABASE mysandbox OWNER mysandbox;
```

2. Configure `.flaskenv`:

```bash
DATABASE_DEFAULT=postgres
DB_URL=localhost
DB_USER=mysandbox
DB_PW=password
DB_NAME=mysandbox
```

3. Initialize database:

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

The instance directory needs to be created:

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

⚠️ **Important**: Change the admin password immediately after first login.

## Verification

After setup, verify the installation:

1. Start the application: `flask run`
2. Open browser to `http://127.0.0.1:9191`
3. Login with admin/admin1234
4. Create a test todo item
5. Verify functionality

All systems operational if you can create and view todo items.
