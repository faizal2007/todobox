# Production Database Migration Fix Guide

## Problem Analysis

The error `Unknown column 'user.api_token' in 'SELECT'` occurs because:

1. **Duplicate migrations**: Two separate migrations added `api_token`:
   - `3e5106ee570c_add_api_token_fields_to_user_model.py` - Adds both `api_token` and `token_created_at`
   - `c682ef478e45_add_api_token_field_to_user_model.py` - Only drops `token_created_at`

2. **Broken migration chain**: The migration `c682ef478e45` assumes `api_token` was already added, but on fresh databases or specific migration states, the column might not exist when the application tries to query it.

3. **Model mismatch**: The `User` model in `app/models.py` declares `api_token` column, but the database doesn't have it due to incomplete migrations.

## Migration Chain (Correct Order)

```bash
6793349c088c (Initial: password_hash size increase)
    ↓
366e5694a9ad (Add OAuth columns)
    ↓
3e5106ee570c (Add api_token + token_created_at)
    ↓
c682ef478e45 (Remove token_created_at)
    ↓
d1f2e3c4b5a6 (Fix: Ensure api_token exists) ← NEW

```python

## Solution: Step-by-Step Fix for Production

### Option A: Fresh Database (Recommended)

If you can reset your production database:

```bash
# 1. Backup your database first
mysqldump -u username -p database_name > backup.sql

# 2. Remove all tables
mysql -u username -p database_name < /dev/null

# 3. Run fresh migrations
flask db upgrade

# 4. Seed initial data
flask seed-db

```sql

### Option B: Existing Database (In-Place Fix)

If you need to preserve existing data:

```bash
# 1. Backup your database
mysqldump -u username -p database_name > backup.sql

# 2. Manually verify and fix the schema
mysql -u username -p database_name

# In MySQL console:
SHOW COLUMNS FROM user;
```sql

If `api_token` column is missing, run:

```sql
ALTER TABLE user ADD COLUMN api_token VARCHAR(255) UNIQUE INDEX NULL;
CREATE UNIQUE INDEX ix_user_api_token ON user(api_token);
```sql

Then run:

```bash
# 3. Update migration history (tell Alembic which migrations have been run)
flask db current  # Check current state

# 4. Run the fix migration
flask db upgrade

```sql

### Option C: Manual Schema Reconstruction (Most Thorough)

```bash
# 1. Backup database
mysqldump -u username -p database_name > backup.sql

# 2. Connect to MySQL
mysql -u username -p

# 3. Drop and recreate tables with correct schema
USE database_name;

# Add missing columns if needed
ALTER TABLE user ADD COLUMN IF NOT EXISTS api_token VARCHAR(255) UNIQUE DEFAULT NULL;
ALTER TABLE user ADD INDEX IF NOT EXISTS ix_user_api_token (api_token);

# 4. Verify schema
DESCRIBE user;
SHOW INDEXES FROM user;
```sql

## How to Apply the Fix

### For Development Environment

```bash
cd /storage/linux/Projects/mysandbox

# 1. Delete the old database
rm instance/todobox.db

# 2. Run fresh migrations
flask db upgrade

# 3. Seed initial data
python -c "from app import db; from app.models import User, Status; User.seed(); Status.seed()"
```python

### For Production Environment

```bash
# 1. Backup current database
mysqldump -u your_user -p your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current migration status
flask db current

# 3. Apply pending migrations
flask db upgrade

# 4. Verify schema
mysql -u your_user -p your_database -e "DESCRIBE user; SHOW INDEXES FROM user WHERE Column_name='api_token';"
```sql

## Verification Checklist

After applying migrations, verify:

```bash
# 1. Check column exists
mysql -u user -p database -e "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='user' AND COLUMN_NAME='api_token';"

# 2. Check index exists
mysql -u user -p database -e "SHOW INDEX FROM user WHERE Column_name='api_token';"

# 3. Test application works
flask run

# 4. Query should work without error
mysql -u user -p database -e "SELECT id, username, email, api_token FROM user;"
```python

## Files Modified

1. `migrations/versions/c682ef478e45_add_api_token_field_to_user_model.py` - Added clarifying comments

1. `migrations/versions/d1f2e3c4b5a6_fix_api_token_column_ensure_api_token.py` - NEW migration to ensure column exists

## Prevention for Future

1. **Use single migration file per feature**: Each feature should have one migration, not multiple

1. **Test migrations before deployment**:

```bash
   # Test on a copy of production database
   mysql -u user -p -e "create database test_db; use test_db; source production_backup.sql;" 
   flask db upgrade --target d1f2e3c4b5a6

```python

1. **Validate model-to-database schema match**:

```bash
   # Add this check before deployment
   from sqlalchemy import inspect
   inspector = inspect(db.engine)
   print(inspector.get_columns('user'))

```python

## Troubleshooting

If you still get the error after running migrations:

```bash
# Check which migrations have been applied
flask db history --rev-range 6793349c088c:d1f2e3c4b5a6

# Get detailed migration status
flask db current
flask db branches
flask db log

# If stuck, rollback to known good state
flask db downgrade -1
flask db upgrade

# Force re-apply specific migration
flask db upgrade d1f2e3c4b5a6

```yaml

## Database Schema Reference

The `user` table should have these columns after all migrations:

| Column | Type | Nullable | Key | Default |
|--------|------|----------|-----|---------|
| id | int | NO | PRIMARY | NULL |
| username | varchar(64) | YES | UNIQUE INDEX | NULL |
| email | varchar(120) | YES | UNIQUE INDEX | NULL |
| fullname | varchar(100) | YES | NULL | NULL |
| password_hash | varchar(255) | YES | NULL | NULL |
| api_token | varchar(255) | YES | UNIQUE INDEX | NULL |
| oauth_provider | varchar(50) | YES | NULL | NULL |
| oauth_id | varchar(255) | YES | INDEX | NULL |

If any columns are missing or have different types, the migrations didn't apply correctly.
