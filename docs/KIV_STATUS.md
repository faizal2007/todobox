# KIV (Keep In View) Status Feature

**Feature Version:** 1.7.0  
**Date Added:** December 5, 2025  
**Status:** Active

---

## Overview

The KIV (Keep In View) status feature allows users to temporarily set aside tasks that require future attention but are not ready to be worked on yet. This feature helps users manage their workflow by separating tasks that need to be kept in view from active and completed tasks.

## What is KIV?

**KIV** stands for "Keep In View" and is a task management status that indicates:

- Tasks that are pending but not immediately actionable
- Tasks waiting for external dependencies or information
- Tasks that need to be reviewed at a later time
- Tasks that are on hold but shouldn't be forgotten

## Key Features

- ✅ **Separate Tab**: KIV tasks appear in their own dedicated tab on the Undone page
- ✅ **Easy Marking**: One-click to mark any task as KIV from the task list
- ✅ **Visual Indicators**: Clock icon (mdi-clock-outline) distinguishes KIV action
- ✅ **Task Counter**: Badge showing the number of KIV tasks
- ✅ **Status Tracking**: Full tracking of when a task was marked as KIV
- ✅ **Dashboard Exclusion**: KIV tasks don't appear in recent tasks on the dashboard

## How to Use

### Marking a Task as KIV

1. **From Today/Tomorrow List**:
   - Find the task you want to mark as KIV
   - Click the clock icon (🕐) next to the task
   - The page will refresh and the task moves to KIV status

2. **From Any Page**:
   - The KIV button is available on all task cards
   - Uses the same clock icon for consistency
   - Loading animation shows while processing

### Viewing KIV Tasks

1. Navigate to **Undone Tasks** page (Menu → Undone)
2. You'll see two tabs:
   - **Uncompleted Tasks**: Active pending tasks
   - **KIV Tasks**: Tasks marked as Keep In View
3. Click the **KIV Tasks** tab to view all KIV tasks
4. The badge shows the count of KIV tasks

### Working with KIV Tasks

From the KIV Tasks tab, you can:

- **View Details**: Click on a task to see full details
- **Edit**: Update task information as needed
- **Complete**: Mark the task as done when ready
- **Re-activate**: Edit the task to change status back to pending
- **Delete**: Remove the task if no longer needed

## Technical Implementation

### Database Structure

**Status Table**:

```sql
id = 9, name = 'kiv'
```sql

The KIV status is stored as status ID 9 in the status table.

### API Endpoints

#### Mark Task as KIV

```http
POST /<todo_id>/kiv
Authorization: Session-based authentication
Content-Type: application/x-www-form-urlencoded
```sql

**Response (200 OK)**:

```json
{
  "status": "Success",
  "todo_id": "task-id"
}
```yaml

#### Alternative Endpoint (with date context)

```http
POST /<date_id>/<todo_id>/kiv
```sql

Where `date_id` can be 'today', 'tomorrow', etc.

### Frontend Implementation

**HTML Structure** (list.html):

```html
<a class="kiv ml-2" data-id='{{ list.Todo.id }}' href="#" 
   data-toggle="tooltip" data-original-title="KIV" 
   aria-label="Mark as KIV">
    <i class="mdi mdi-clock-outline kiv-icon"></i>
    <span class="kiv-loading" style="display: none;">
        <i class="mdi mdi-loading mdi-spin"></i>
    </span>
    <span class="sr-only">Mark as KIV</span>
</a>
```yaml

**JavaScript Handler**:

```javascript
document.querySelectorAll('.kiv').forEach(function(button) {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        var todoId = this.dataset.id;
        var icon = this.querySelector('.kiv-icon');
        var loading = this.querySelector('.kiv-loading');
        
        // Show loading state
        if (icon) icon.style.display = 'none';
        if (loading) loading.style.display = '';
        button.disabled = true;
        
        fetch('/' + todoId + '/kiv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: '_csrf_token=' + encodeURIComponent(csrfToken)
        })
        .then(function() {
            window.location.href = "/list/today";
        })
        .catch(function(error) {
            console.error('Error marking todo as kiv:', error);
            // Restore button state on error
            if (icon) icon.style.display = '';
            if (loading) loading.style.display = 'none';
            button.disabled = false;
        });
    });
});
```python

### Backend Implementation

**Route Handler** (app/routes.py):

```python
@app.route('/<path:todo_id>/kiv', methods=['POST'])
@login_required
def mark_kiv(todo_id):
    """Mark a todo as kiv from any page"""
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if todo:
        date_entry = datetime.now()
        todo.modified = date_entry
        db.session.commit()
        Tracker.add(todo.id, 9, date_entry)  # Status 9 = KIV
        
        return jsonify({
            'status': 'Success',
            'todo_id': todo.id if todo else None
        }), 200
```python

**Filtering KIV Tasks** (app/routes.py):

```python
@app.route('/undone')
@login_required
def undone():
    """Show all undone/pending todos across all dates"""
    undone_todos = []
    kiv_todos = []
    all_todos = Todo.query.filter_by(user_id=current_user.id)\
                          .order_by(Todo.modified.desc()).all()
    
    for todo in all_todos:
        latest_tracker = Tracker.query.filter_by(todo_id=todo.id)\
                                      .order_by(Tracker.timestamp.desc())\
                                      .first()
        
        if latest_tracker:
            if latest_tracker.status_id != 6 and latest_tracker.status_id != 9:
                # Uncompleted tasks (not done, not KIV)
                undone_todos.append((todo, latest_tracker))
            elif latest_tracker.status_id == 9:
                # KIV tasks
                kiv_todos.append((todo, latest_tracker))
    
    return render_template('undone.html', 
                         title='Undone Tasks',
                         todos=undone_todos,
                         kiv_todos=kiv_todos)
```python

## UI Design

### Visual Elements

- **Icon**: Clock outline icon (mdi-clock-outline)
- **Color**: Default link color (changes to primary color on hover)
- **Badge**: Secondary badge color for KIV tab counter
- **Loading State**: Spinning icon during processing

### Accessibility

- **ARIA Label**: "Mark as KIV" for screen readers
- **Tooltip**: Shows "KIV" on hover
- **Screen Reader Text**: Hidden span with descriptive text
- **Keyboard Navigation**: Fully accessible via keyboard

## Use Cases

### 1. Waiting for Information

**Scenario**: You're working on a project proposal but need approval from management.

**Action**: Mark the task as KIV until you receive the necessary approval.

### 2. Blocked Tasks

**Scenario**: A task depends on another team completing their work first.

**Action**: Mark as KIV to keep it visible but separate from active work.

### 3. Future Planning

**Scenario**: You have ideas for future enhancements but they're not current priorities.

**Action**: Mark as KIV to review during planning sessions.

### 4. Seasonal Tasks

**Scenario**: Tasks that are only relevant at certain times of the year.

**Action**: Mark as KIV during off-season, review when relevant.

## Filtering and Queries

### Dashboard Filter

KIV tasks are excluded from the "Recent Todos" section on the dashboard:

```python
# Dashboard query excludes status_id = 9 (KIV)
recent_todos = db.session.query(Todo, Tracker).join(
    Tracker, Todo.id == Tracker.todo_id
).filter(
    Todo.user_id == current_user.id,
    Tracker.timestamp == Todo.modified,
    Tracker.status_id != 6,  # Not done
    Tracker.status_id != 9   # Not KIV
).order_by(Todo.modified.desc()).limit(5).all()
```python

## Best Practices

### When to Use KIV

✅ **Good Uses**:
- Tasks waiting for external input
- Ideas to revisit later
- Tasks blocked by dependencies
- Low-priority items to review periodically

❌ **Avoid Using KIV For**:
- Tasks you want to complete soon (use normal pending status)
- Completed tasks (use done status)
- Tasks you'll never do (delete them instead)

### Task Management Workflow

1. **Create Task**: Start as pending/new status
2. **Work on Task**: Keep as pending while actively working
3. **Need to Pause**: Mark as KIV if blocked or waiting
4. **Resume Work**: Change status back to pending when ready
5. **Complete**: Mark as done when finished

## Troubleshooting

### KIV Button Not Working

**Problem**: Clicking the KIV button doesn't move the task.

**Solutions**:
- Check browser console for JavaScript errors
- Ensure CSRF token is valid (refresh the page)
- Verify you're logged in (session might have expired)
- Check network tab for failed requests

### KIV Tasks Not Appearing

**Problem**: Tasks marked as KIV don't show in the KIV tab.

**Solutions**:
- Refresh the Undone page
- Check that the task wasn't accidentally deleted
- Verify the task belongs to your account
- Check database: `SELECT * FROM tracker WHERE status_id = 9;`

### Can't Move Task Out of KIV

**Problem**: Unable to change status from KIV to pending.

**Solutions**:
- Edit the task and update any field (triggers status update option)
- Mark as done, then edit again to set back to pending
- Use the API to manually update the status

## Related Documentation

- **[MODELS.md](MODELS.md)** - Database schema and status table
- **[API.md](API.md)** - Complete API endpoint reference
- **[OVERVIEW.md](OVERVIEW.md)** - Project features overview

## Version History

### Version 1.7.0 (December 5, 2025)

- Initial implementation of KIV status feature
- Added dedicated KIV tab on Undone page
- Implemented API endpoints for KIV marking
- Added UI elements (button, icon, loading state)
- Dashboard filtering to exclude KIV tasks
- Full tracking support via Tracker model

---

**Last Updated:** December 5, 2025  
**Status:** Complete and Active ✅
