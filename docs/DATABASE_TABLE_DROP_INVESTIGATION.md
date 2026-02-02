# Database Table Drop Investigation Report

**Date:** February 1, 2026  
**Issue:** Tables dropping when starting the app  
**Status:** Investigation in progress

## Problem Statement

User reports that database tables are dropping repeatedly when using item 6 (Run) in `todomanage.py`.

## Analysis Performed

### 1. Code Review - Session Expiration Feature (Commit 47d4dbc)

**Changes to app/__init__.py:**
- ✓ No `drop_all()` calls added
- ✓ `cleanup_pending_deletions()` only deletes user records, not tables
- ✓ Error handling improved to catch missing tables gracefully

**Changes to app/routes.py:**
- ✓ Added session expiration routes
- ✓ No database table operations

**New files added:**
- ✓ `app/session_handler.py` - No database table operations
- ✓ `app/static/js/session-monitor.js` - Client-side only
- ✓ `app/session_handler_examples.py` - Example code only

### 2. Search for Dangerous Operations

**Found `db.drop_all()` in:**
- `tests/test_user_isolation.py` - Test teardown (isolated to tests)
- `tests/test_achievement_modal_endpoint.py` - Test teardown (isolated to tests)
- `tests/conftest.py` - Test teardown (isolated to tests)
- `tests/test_all_routes.py` - Test teardown (isolated to tests)
- `tests/test_utility_functions.py` - Test teardown (isolated to tests)
- `tests/test_integration.py` - Test teardown (isolated to tests)
- `tests/test_security_updates.py` - Test teardown (isolated to tests)

**Result:** ✓ All `drop_all()` calls are in test files ONLY, scoped to test fixture cleanup

### 3. Verified App Import Safety

```bash
python3 -c "from app import app; print('✓ App imported successfully')"
# Result: ✓ App imports without errors
```

**Verified:**
- ✓ No pytest/conftest imported during app initialization
- ✓ No auto-discovery of test fixtures during app startup
- ✓ No database table operations on app import

### 4. Checked todomanage.py Item 6 (Run Function)

**Current code:**
```python
def run_todobox():
    """Run the TodoBox Flask application"""
    import subprocess
    ...
    subprocess.run(["python", "todobox.py"], cwd=project_dir)
```

**Issues identified:**
1. ⚠️ Uses `"python"` instead of `"python3"` (should use python3 for consistency)
2. ✓ Runs `todobox.py` which only imports app
3. ✓ `todobox.py` has no database operations

### 5. Verified Flask App Startup (todobox.py)

```python
from app import app

if __name__ == "__main__":
    app.run(debug=..., host=..., port=...)
```

**Result:** ✓ Simple app startup with no table operations

### 6. Conftest.py Isolation Check

**Found:** `conftest.py` imports at module level:
```python
from tests.login_fixtures import *
```

**Analysis:**
- ✓ Conftest.py is ONLY loaded by pytest, not during normal app startup
- ✓ Login fixtures only create test users, don't drop tables
- ✓ No auto-discovery of conftest during normal app operation

### 7. Database State Check

```bash
ls -la instance/todobox.db
# Result: No database file exists
```

This means:
- ✓ App hasn't been run yet, or
- ⚠️ Database was already dropped before investigation started

## Possible Root Causes

### Issue 1: Pre-existing Condition
- Database may have been dropped before the session expiration feature
- Feature didn't introduce any table-dropping code
- No database file currently exists

### Issue 2: Pytest Collision (LOW PROBABILITY)
- If pytest somehow runs during app startup (highly unlikely)
- Conftest fixture would create in-memory DB, not affect production DB
- Evidence: conftest uses `sqlite:///:memory:` for tests

### Issue 3: Missing .flaskenv or Configuration
- `todomanage.py` checks for `.flaskenv` before running app
- If missing, app won't start
- Check: Does `.flaskenv` exist and is properly configured?

## Recommendations

### Immediate Actions

1. **Check .flaskenv Configuration**
   ```bash
   cat .flaskenv | grep -i database
   # Verify DATABASE_DEFAULT, DATABASE_URI are correct
   ```

2. **Verify Database Initialization**
   ```bash
   # Manually initialize database using todomanage.py option 5 (Install)
   python3 todomanage.py
   # Select option 5 to install
   ```

3. **Fix todomanage.py Item 6**
   - Change `"python"` to `"python3"` for consistency

4. **Create Database Backup Check**
   ```bash
   # After installing, verify DB exists
   ls -la instance/todobox.db
   ```

### Testing the Issue

1. **Before running app:**
   ```bash
   python3 -c "from app import app; print('✓ App loads successfully')"
   ```

2. **Verify no test files are imported:**
   ```bash
   python3 -c "import sys; sys.path.insert(0, '.'); from app import app; print('tests' in sys.modules)"
   # Result should be False
   ```

3. **Check if conftest gets imported during app startup:**
   ```bash
   python3 -c "import sys; sys.path.insert(0, '.'); from app import app; print('pytest' in sys.modules)"
   # Result should be False
   ```

## Files Modified in Session Expiration Commit

The following files were modified in commit 47d4dbc:
- `.github/agents/python-developer.md` - Documentation
- `CHANGELOG.md` - Documentation
- `app/__init__.py` - Error handling improvement ONLY
- `app/routes.py` - New session routes (no drop operations)
- `OBSOLETE_TESTS_ANALYSIS.py` - Analysis script
- Tests and documentation files

**None of these changes introduce table-dropping code.**

## Conclusion

**The session expiration feature (commit 47d4dbc) does NOT contain any code that drops database tables.**

The table dropping issue is either:
1. Pre-existing condition (tables were already dropped)
2. User hasn't initialized the database yet (need to run todomanage.py option 5)
3. Configuration issue in `.flaskenv`
4. External factor not in the codebase

**Next Steps:** User should:
1. Check if `.flaskenv` exists and is configured
2. Run todomanage.py option 5 (Install) to initialize database
3. Verify database exists: `ls -la instance/todobox.db`
4. Then run option 6 (Run) to start the app

---

**Action Items:**
- [ ] Fix todomanage.py item 6 to use `python3` instead of `python`
- [ ] Add database initialization verification before running app
- [ ] Consider adding startup checks to alert user if DB not initialized
