# KIV Table Refactoring - COMPREHENSIVE PLAN

## Current Problem

Your system mixes KIV (Keep In View) as **status_id=9** with regular statuses:
- ❌ KIV logic mixed with regular status tracking
- ❌ Querying for KIV requires filtering on status_id
- ❌ Complex transitions: KIV ↔ other statuses
- ❌ Bug: Can't save KIV tasks to other dates
- ❌ Hard to manage KIV separately

**Result**: Multiple redirect bugs, status confusion, hard to maintain

---

## New Design

Create a **separate KIV table** to cleanly manage KIV todos:

### Old Structure
```
Tracker table tracks todo status changes:
- status_id = 5 (new)
- status_id = 6 (done)
- status_id = 8 (re-assign)
- status_id = 9 (KIV)  ← Mixed with other statuses

Problem: KIV is just another status, no special handling
```

### New Structure
```
Tracker table - tracks regular status changes only:
- status_id = 5 (new)
- status_id = 6 (done)
- status_id = 8 (re-assign)
- No KIV status here!

KIV table - separate, explicit KIV management:
- todo_id: which todo is in KIV
- user_id: which user's KIV
- entered_at: when entered KIV
- exited_at: when exited KIV (for history)
- is_active: whether currently in KIV

Benefit: Clean separation, easy to query, easy to manage
```

---

## What Changes

### 1. Database Schema

**New KIV Table**:
```sql
CREATE TABLE kiv (
    id INT PRIMARY KEY AUTO_INCREMENT,
    todo_id INT UNIQUE NOT NULL,
    user_id INT NOT NULL,
    entered_at DATETIME NOT NULL DEFAULT NOW(),
    exited_at DATETIME,
    is_active BOOL NOT NULL DEFAULT TRUE,
    FOREIGN KEY (todo_id) REFERENCES todo(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    INDEX (user_id),
    INDEX (is_active),
    INDEX (entered_at)
);
```

**Status Table Update**:
- Keep status_id=9 for backward compatibility
- Can remove it in future migration after KIV table is fully tested

### 2. Code Changes

**Instead of**:
```python
# Check if todo is KIV
if latest_tracker.status_id == 9:
    # It's KIV
```

**Use**:
```python
# Check if todo is KIV
if KIV.is_kiv(todo_id):
    # It's KIV
```

**Instead of**:
```python
# Make todo KIV
Tracker.add(todo_id, 9, date)  # status 9 = KIV
```

**Use**:
```python
# Make todo KIV
KIV.add(todo_id, current_user.id)
```

**Instead of**:
```python
# Exit KIV
Tracker.add(todo_id, 5, date)  # Change to status 5
```

**Use**:
```python
# Exit KIV
KIV.remove(todo_id)
Tracker.add(todo_id, 5, date)  # Add regular status
```

### 3. Query Changes

**Before**:
```python
# Get KIV todos
kiv_todos = Todo.query.filter(
    Tracker.status_id == 9
).all()
```

**After**:
```python
# Get KIV todos
kiv_todos = Todo.query.join(KIV).filter(
    KIV.is_active == True,
    Todo.user_id == current_user.id
).all()
```

---

## Migration Steps

### Phase 1: Add New KIV Table (Current)
1. ✅ Create KIV model
2. ⏳ Create Alembic migration
3. ⏳ Run migration: `flask db upgrade`
4. ⏳ Migrate existing KIV todos from status_id=9 to KIV table

### Phase 2: Update Routes
1. Update all `status_id == 9` checks to `KIV.is_kiv(todo_id)`
2. Update all KIV status changes to use `KIV.add()` and `KIV.remove()`
3. Test thoroughly

### Phase 3: Update Queries
1. Update undone/KIV page query
2. Update dashboard queries
3. Update filtering logic

### Phase 4: Clean Up (Future)
1. Remove status_id=9 from Status table
2. Remove any remaining status_id=9 references
3. Remove Status model if no longer needed

---

## Benefits

### Cleaner Code
```
BEFORE:
if latest_tracker.status_id == 9:
    # Do KIV logic
    Tracker.add(todo_id, 5, date)

AFTER:
if KIV.is_kiv(todo_id):
    # Do KIV logic
    KIV.remove(todo_id)
    Tracker.add(todo_id, 5, date)
```

### Easier Debugging
- KIV todos in one table
- Regular statuses in another
- No confusion about what KIV means

### Easier Queries
- Find KIV todos: `KIV.query.filter(is_active=True).all()`
- Find non-KIV todos: `join(KIV) with is_active=False or no join`
- History tracking: `exited_at` shows when user exited KIV

### Fixes Current Bugs
- Clear distinction between KIV and scheduled tasks
- No mixed status confusion
- Easier to handle transitions (KIV → today, KIV → tomorrow, etc.)

---

## Database Migration Details

The migration will:
1. Create new `kiv` table with proper structure
2. Automatically migrate existing KIV todos (status_id=9)
3. Keep status_id=9 for backward compatibility

**To run the migration**:
```bash
cd /storage/linux/Projects/python/mysandbox
source venv/bin/activate
flask db upgrade
```

---

## Files That Need Updates

### Phase 1 (Done)
- ✅ `app/models.py` - Added KIV model
- ✅ `migrations/versions/kiv_table_migration.py` - Created migration

### Phase 2 (To Do)
- `app/routes.py` - Update all KIV checks
  - Line 720: Remove status_id != 9 from query
  - Line 1211, 1214: Update KIV checks
  - Line 1517, 1548, 1562, 1592: Update KIV checks

### Phase 3 (To Do)
- `app/models.py` - Update Todo.getList() query
- `app/templates/undone.html` - Uses KIV query data

---

## Testing After Migration

**Test 1: KIV Add/Remove**
```python
KIV.add(todo_id, user_id)
assert KIV.is_kiv(todo_id) == True
KIV.remove(todo_id)
assert KIV.is_kiv(todo_id) == False
```

**Test 2: KIV Transition to Tomorrow**
```
1. Create todo
2. Make it KIV
3. Edit and schedule to tomorrow
4. Verify KIV.is_kiv(todo_id) == False
5. Verify todo in tomorrow list
```

**Test 3: KIV Transition to Today**
```
1. Create todo
2. Make it KIV
3. Edit and schedule to today
4. Verify KIV.is_kiv(todo_id) == False
5. Verify todo in today list
```

---

## Rollback Plan

If issues occur:
```bash
# Rollback migration
flask db downgrade

# This will drop the KIV table
# Existing code using KIV model will fail gracefully
```

---

## Next Steps

1. Run migration to create KIV table
2. Update routes.py to use KIV model
3. Update queries to use KIV table
4. Test thoroughly
5. Remove old status_id=9 logic

---

## Why This Works Better

| Aspect | Old Way | New Way |
|--------|---------|---------|
| KIV Storage | Mixed status | Separate table |
| KIV Query | Filter status_id=9 | Join KIV table |
| KIV Transition | Add new Tracker status | Remove from KIV, add new status |
| Code Clarity | Confusing | Clear intent |
| Bug Prone | High | Low |
| Maintenance | Hard | Easy |

---

## Expected Bugs Fixed

1. ✅ Can't save KIV task to tomorrow (will be fixed)
2. ✅ Can't save KIV task to today (will be fixed)
3. ✅ Redirect confusion (clearer logic flow)
4. ✅ Status confusion (separated concerns)

This refactoring will make the codebase much more maintainable and fix the root cause of KIV-related bugs.
