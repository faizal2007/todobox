# First-Time User Creation Guide

## Overview

This guide covers creating users for the MySandbox application on first-time setup. There are **three methods** available:

1. **Interactive Python Script** (Recommended for first-time setup)
2. **Flask CLI Commands** (Recommended for administration)
3. **Manual Database Entry** (Emergency/advanced)

---

## ⭐ Method 1: Interactive Python Script (Recommended)

### When to Use

- First-time application setup
- Initial admin user creation
- Interactive prompts with validation

### Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the interactive script
python3 create_user.py
```

### Features

- ✅ Automatic admin detection
- ✅ Interactive username/email validation
- ✅ Password strength checking
- ✅ Duplicate account prevention
- ✅ Clear visual feedback
- ✅ User-friendly prompts

### Workflow

#### First Time (No Admin Exists)

```bash
$ python3 create_user.py

============================================================
  MySandbox - First Time User Creation
============================================================

Creating ADMIN user (first-time setup)
------------------------------------------------------------

Use default admin user? (username: admin, email: admin@examples.com) [Y/n]: 

✓ Username: admin
✓ Email: admin@examples.com

Enter password: ••••••••
Confirm password: ••••••••
✓ Password is valid (strength: moderate)

------------------------------------------------------------
Confirm user details:
  Username: admin
  Email: admin@examples.com
  Password: ••••••••
------------------------------------------------------------

Create this user? [Y/n]: y

✅ Admin user 'admin' created successfully!

============================================================
✅ User creation completed successfully!
============================================================
```

#### Admin Already Exists

```bash
⚠️  Admin user already exists!
   Username: admin
   Email: admin@examples.com

Options:
  1) Reset admin password
  2) Create a different user
  3) Exit

Select option (1-3): 2
```

### Validation Rules

| Field | Rules |
|-------|-------|
| Username | 3-64 chars, alphanumeric + _ - |
| Email | Valid format, unique |
| Password | Min 8 chars, must match confirmation |

### Example Session: Create Custom Admin

```bash
$ python3 create_user.py

Use default admin user? [Y/n]: n

Username: john_admin
✓ Username 'john_admin' is valid

Email: john@company.com
✓ Email 'john@company.com' is valid

Enter password: ••••••••••••
Confirm password: ••••••••••••
✓ Password is valid

------------------------------------------------------------
Confirm user details:
  Username: john_admin
  Email: john@company.com
  Password: ••••••••••••
------------------------------------------------------------

Create this user? [Y/n]: y

✅ Admin user 'john_admin' created successfully!
```

---

## 📋 Method 2: Flask CLI Commands

### Best For

- Ongoing user management
- Scripted/automated setups
- Administrative tasks

### Available Commands

#### Create User (Interactive)

```bash
flask create-user
```

**Example:**

```bash
$ flask create-user

============================================================
  MySandbox - User Creation
============================================================

Username: alice
Email: alice@company.com
Password: ••••••••
Confirm password: ••••••••

------------------------------------------------------------
Confirm user details:
  Username: alice
  Email: alice@company.com
------------------------------------------------------------

Create this user? [y/N]: y

✅ User "alice" created successfully!
```

#### Create User (Non-Interactive)

```bash
flask create-user --username bob --email bob@company.com --password SecurePass123
```

#### Reset Password

```bash
flask reset-password --username admin
```

**Example:**

```bash
$ flask reset-password --username admin

📝 Resetting password for user: admin
Enter current password to verify: ••••••••
New password: ••••••••••••
Confirm password: ••••••••••••

✅ Password for "admin" updated successfully!
```

#### List All Users

```bash
flask list-users
```

**Output:**

```bash
============================================================
  Users
============================================================
ID    Username             Email                     Full Name
------------------------------------------------------------
1     admin                admin@examples.com        (not set)
2     alice                alice@company.com         Alice Smith
3     bob                  bob@company.com           Bob Jones
============================================================
```

#### Delete User

```bash
flask delete-user
```

**Example:**

```bash
$ flask delete-user

Username: bob

⚠️  Are you sure you want to delete user "bob"? This cannot be undone. [y/N]: y

✅ User "bob" deleted successfully!
```

---

## 🔧 Method 3: Manual Database Entry

### Use Cases

- Emergency situations
- Direct database access needed
- SQLite development environments

### For SQLite

```bash
# Open database
sqlite3 instance/mysandbox.db

# Create user
sqlite> INSERT INTO "user" (username, email, password_hash) 
VALUES ('admin', 'admin@examples.com', 'pbkdf2:sha256:...');
```

### For MySQL

```bash
# Connect to database
mysql -u freakie -p -h 192.168.1.112 shimasu_db

# Create user
INSERT INTO user (username, email, password_hash) 
VALUES ('admin', 'admin@examples.com', 'pbkdf2:sha256:...');
```

**⚠️ Note:** Password hash must be generated using Werkzeug's `generate_password_hash()` function. Use Python:

```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash('admin1234')
print(password_hash)
```

---

## 🚀 First-Time Setup Workflow

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd /storage/linux/Projects/mysandbox

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Database

```bash
# Copy environment file
cp .flaskenv.example .flaskenv

# Edit .flaskenv with your database details
nano .flaskenv
```

### Step 3: Initialize Database

```bash
# Run migrations
flask db upgrade
```

### Step 4: Create Admin User

```bash
# Run interactive script (RECOMMENDED)
python3 create_user.py

# OR use Flask CLI
flask create-user
```

### Step 5: Verify & Start

```bash
# List users to verify creation
flask list-users

# Start application
flask run
```

### Step 6: Login

```bash
Open browser: http://127.0.0.1:9191
Username: admin (or your custom username)
Password: (the password you set)
```

### Step 7: Change Password

After first login, go to `/security` and change the password.

---

## ✅ Post-Creation Checklist

After creating the admin user:

- [ ] User created successfully
- [ ] User can login
- [ ] User appears in `flask list-users`
- [ ] Password works correctly
- [ ] Can navigate to todos page
- [ ] Change password in `/security` page
- [ ] Create test todo item

---

## 🔐 Security Best Practices

### First-Time Setup

1. ✅ **Never use default credentials in production**
   - Create unique admin username
   - Use strong password (12+ characters)

2. ✅ **Change password immediately**
   - Login after creation
   - Go to `/security` page
   - Set strong password

3. ✅ **Protect database credentials**
   - Store `.flaskenv` securely
   - Don't commit to version control
   - Use environment variables in production

### User Management

1. ✅ **Validate all inputs**
   - Email format checking
   - Username uniqueness
   - Password strength requirements

2. ✅ **Use secure passwords**
   - Minimum 8 characters
   - Mix of upper, lower, numbers, symbols
   - Avoid dictionary words

3. ✅ **Audit user list regularly**
   - Run `flask list-users` periodically
   - Delete unused accounts
   - Monitor for suspicious usernames

---

## 🐛 Troubleshooting

### "User already exists"

**Problem:** Username or email already registered

**Solution:**

1. Use different username/email
2. Or reset password with `flask reset-password`
3. Or delete user with `flask delete-user`

```bash
# Check existing users
flask list-users

# Delete conflicting user
flask delete-user --username old_admin

# Try again
python3 create_user.py
```

### "Database not found"

**Problem:** Database not created yet

**Solution:**

```bash
# Run migrations first
flask db upgrade

# Then create user
python3 create_user.py
```

### "Password hash mismatch"

**Problem:** Password verification fails

**Solution:**

```bash
# Reset password
flask reset-password --username admin

# OR delete and recreate user
flask delete-user --username admin
python3 create_user.py
```

### "Permission denied"

**Problem:** No database write permissions

**Solution:**

```bash
# Check file permissions
ls -la instance/
chmod 755 instance/
chmod 644 instance/mysandbox.db

# Or for directory:
chmod 755 migrations/versions/
```

### "Invalid email format"

**Problem:** Email validation failed

**Solution:**

- Use proper email format: `user@domain.com`
- Check for typos
- Ensure no spaces

**Valid examples:**

- `admin@example.com` ✅
- `user+tag@company.co.uk` ✅
- `invalid@email` ❌
- `user @example.com` ❌

---

## 📝 Example Scenarios

### Scenario 1: Initial Setup with Default Admin

```bash
source venv/bin/activate
flask db upgrade
python3 create_user.py
# Select: Use default admin? [Y/n]: y
# Create admin / admin@examples.com
```

### Scenario 2: Initial Setup with Custom Admin

```bash
source venv/bin/activate
flask db upgrade
python3 create_user.py
# Select: Use default admin? [Y/n]: n
# Create custom username/email/password
```

### Scenario 3: Add Team Members

```bash
# User 1
flask create-user --username alice --email alice@company.com

# User 2
flask create-user --username bob --email bob@company.com

# User 3
flask create-user

# Verify
flask list-users
```

### Scenario 4: Reset Forgotten Password

```bash
# Admin forgot password
flask reset-password --username admin
# Provide current password (or use delete/recreate if needed)

# Alternative: Delete and recreate
flask delete-user --username admin
python3 create_user.py
```

### Scenario 5: Automated Setup (CI/CD)

```bash
#!/bin/bash
source venv/bin/activate
flask db upgrade
flask create-user --username admin --email admin@example.com --password AutoGenerated123
```

---

## 📚 Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `python3 create_user.py` | Interactive script | `python3 create_user.py` |
| `flask create-user` | Create user (interactive) | `flask create-user` |
| `flask reset-password` | Change password | `flask reset-password --username admin` |
| `flask list-users` | Show all users | `flask list-users` |
| `flask delete-user` | Remove user | `flask delete-user` |

---

## Next Steps

After creating users:

1. **Start Application**

   ```bash
   flask run
   ```

2. **Login**
   - URL: [http://127.0.0.1:9191](http://127.0.0.1:9191)
   - Use created credentials

3. **Create Todos**
   - Go to `/todo` page
   - Create test items

4. **Explore Features**
   - Mark todos as done
   - Update account settings
   - Change password

5. **Deploy**
   - See DEPLOYMENT.md for production setup

---

**Version:** 1.0
**Last Updated:** November 25, 2025
**Status:** Production Ready
