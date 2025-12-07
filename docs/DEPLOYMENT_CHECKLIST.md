# Production Deployment Checklist - API Token Migration Fix

## Pre-Deployment (Before you deploy the fix)

- [ ] **Read** `MIGRATION_FIX_SUMMARY.md`
- [ ] **Read** `MIGRATION_ANALYSIS.md` to understand the issue
- [ ] **Backup** production database:

```bash
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql
# Store this backup safely!
```sql

- [ ] **Test** migrations on a development/staging copy of production database
- [ ] **Notify** team about scheduled deployment

## Deployment Steps (Execute in order)

### 1. Stop Application (If Needed)

```bash
# If using systemd
systemctl stop todobox

# If using supervisor  
supervisorctl stop todobox

# If using gunicorn manually
# gracefully stop the process

```bash

### 2. Deploy New Code

```bash
cd /path/to/todobox

# Pull latest changes
git pull origin master

# Or if using manual deployment:
# Copy the new migration file:
# migrations/versions/d1f2e3c4b5a6_fix_api_token_column_ensure_api_token.py

```python

### 3. Verify Migration Files

```bash
# Check all migration files are in place
ls -la migrations/versions/

# Should see:
# ✅ 6793349c088c_increase_password_hash_column_size_to_.py
# ✅ 366e5694a9ad_add_oauth_columns_to_user_model.py
# ✅ 3e5106ee570c_add_api_token_fields_to_user_model.py
# ✅ c682ef478e45_add_api_token_field_to_user_model.py
# ✅ d1f2e3c4b5a6_fix_api_token_column_ensure_api_token.py  ← NEW

```python

### 4. Check Database Before Migration

```bash
# Connect to production database
mysql -u username -p database_name

# Check current schema
DESCRIBE user;

# Check if api_token exists
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME='user' AND COLUMN_NAME='api_token';

# Check migration history
# (From Flask):
# flask db history

```sql

### 5. Run Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Set production environment
export FLASK_ENV=production
export DATABASE_URL=mysql://user:pass@host/dbname

# Run migrations
flask db upgrade

# Expected output:
# INFO [alembic.runtime.migration] Context impl MySQLImpl.
# INFO [alembic.runtime.migration] Will assume non-transactional DDL.
# INFO [alembic.migration] Running upgrade 6793349c088c -> 366e5694a9ad
# INFO [alembic.migration] Running upgrade 366e5694a9ad -> 3e5106ee570c
# INFO [alembic.migration] Running upgrade 3e5106ee570c -> c682ef478e45
# INFO [alembic.migration] Running upgrade c682ef478e45 -> d1f2e3c4b5a6  ← NEW

```sql

### 6. Verify Migration Completed

```bash
# Check current migration status
flask db current
# Should show: d1f2e3c4b5a6

# Verify column exists
mysql -u username -p database_name \
  -e "DESCRIBE user WHERE Field='api_token';"

# Verify index exists
mysql -u username -p database_name \
  -e "SHOW INDEX FROM user WHERE Column_name='api_token';"
```sql

### 7. Start Application

```bash
# Start the service
systemctl start todobox

# Or supervisor
supervisorctl start todobox

# Or manually (for testing)
flask run --host=0.0.0.0 --port=5000

```sql

### 8. Post-Deployment Verification

```bash
# Test 1: Check application starts without errors
curl http://your-domain/

# Test 2: Check logs for errors
tail -f /var/log/todobox/app.log

# Test 3: Test login (api_token column should work)
# Use your application's login feature

# Test 4: Database query test
python3 << 'EOF'
from app import app, db
from app.models import User

with app.app_context():
    try:
        # This query uses api_token column
        users = db.session.execute(
            db.select(User).limit(1)
        ).scalars().first()
        
        if users:
            print(f"✅ User query successful")
            print(f"   ID: {users.id}")
            print(f"   Username: {users.username}")
            print(f"   API Token: {users.api_token}")
        else:
            print("✅ Database query works (no users yet)")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
EOF

# Test 5: Check API token functionality
python3 << 'EOF'
from app import app, db
from app.models import User

with app.app_context():
    try:
        user = db.session.execute(
            db.select(User).limit(1)
        ).scalars().first()
        
        if user:
            # Generate a new token
            token = user.generate_api_token()
            print(f"✅ API token generated: {token[:10]}...")
        else:
            print("⚠️  No users in database")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
EOF

```yaml

## Monitoring Post-Deployment

### Logs to Watch

```bash
# Application logs
tail -f /var/log/todobox/app.log

# MySQL error log
tail -f /var/log/mysql/error.log

# System logs
journalctl -u todobox -f

```sql

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Unknown column" error persists | Run `flask db upgrade` again, verify migration status with `flask db current` |
| Application won't start | Check logs: `tail -f /var/log/todobox/app.log` |
| Slow database response | Migration is running, wait for completion (can take minutes on large tables) |
| Connection refused | Ensure database is accessible: `mysql -u user -p -h host database` |

### Rollback Procedure (If needed)

```bash
# 1. Stop the application
systemctl stop todobox

# 2. Restore database from backup
mysql -u username -p database_name < backup_YYYYMMDD_HHMMSS.sql

# 3. Rollback migrations
flask db downgrade -1

# 4. Deploy previous version of code
git checkout HEAD~1

# 5. Start application
systemctl start todobox

# 6. Verify it works
curl http://your-domain/
```sql

## Post-Deployment Checklist

- [ ] Application starts without errors
- [ ] Can login to application
- [ ] No "Unknown column" errors in logs
- [ ] Database queries work normally
- [ ] API token features work (if used)
- [ ] All user features functional
- [ ] Team notified of successful deployment

## Verification Commands Quick Reference

```bash
# Check migration status
flask db current

# View all migrations
flask db history

# View migration branches
flask db branches

# Verify column exists
mysql -u user -p db -e "DESCRIBE user;" | grep api_token

# Verify index exists
mysql -u user -p db -e "SHOW INDEX FROM user;" | grep api_token

# Check for any SQL errors
mysql -u user -p db -e "SELECT * FROM alembic_version;"
```sql

## Support Contact

If you encounter issues:

1. **Check logs first**: `tail -f /var/log/todobox/app.log`
2. **Read troubleshooting section** in `MIGRATION_FIX_GUIDE.md`
3. **Restore from backup** if critical
4. **Contact support** with error details and logs

## Success Criteria

✅ Migration completed without errors
✅ Application starts normally  
✅ No "Unknown column" errors
✅ Database queries work
✅ All features functional

---

**Deployment Date:** [Your date]
**Deployed By:** [Your name]
**Status:** Ready for production
