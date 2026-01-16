# Achievement Modal - Time Taken Calculation

## What is "Time Taken"?

The **"Time Taken"** field in the achievement modal shows **how many hours** it took from when you created the todo until you marked it as done.

---

## How It's Calculated

### Status IDs (Key to Understanding)

The system tracks todo status with these IDs:
- **Status ID 5:** "New" - when todo is created
- **Status ID 6:** "Done" - when todo is marked as complete
- **Status ID 7:** "Failed"
- **Status ID 8:** "Re-assign"
- **Status ID 9:** "KIV" (Keep In View)

### The Calculation Formula

```
Time Taken = Timestamp(Done) - Timestamp(Created)
           = When marked done - When created
           = Converted to hours (rounded to 1 decimal place)
```

### Code Location

**File:** [app/routes.py](app/routes.py#L2007-L2010)

```python
# Get the creation tracker (when todo was created)
creation_tracker = Tracker.query.filter_by(
    todo_id=todo_id,
    status_id=5  # "New" status - when created
).order_by(Tracker.timestamp.asc()).first()

# Get the completion tracker (when todo was marked done)
completion_tracker = Tracker.query.filter_by(
    todo_id=todo_id,
    status_id=6  # "Done" status - when completed
).order_by(Tracker.timestamp.desc()).first()

# Calculate the difference in hours
time_to_complete = None
if creation_tracker and completion_tracker:
    time_diff = completion_tracker.timestamp - creation_tracker.timestamp
    # Convert seconds to hours, rounded to 1 decimal place
    time_to_complete = round(time_diff.total_seconds() / 3600, 1)
```

---

## Example Calculation

### Scenario
- **Created:** January 15, 2024 at 2:00 PM
- **Marked Done:** January 15, 2024 at 5:30 PM

### Math
```
Time Difference = 5:30 PM - 2:00 PM
                = 3 hours 30 minutes
                = 3.5 hours
                
In seconds: 3.5 * 3600 = 12,600 seconds
Rounded to 1 decimal: 3.5 hours
```

### Display in Modal
```
Time Taken: 3h 30m
```

---

## How It's Displayed in the Modal

**File:** [app/templates/achievements.html](app/templates/achievements.html#L628-L638)

```javascript
if (todoData.time_to_complete !== null && todoData.time_to_complete !== undefined) {
    const hours = Math.floor(todoData.time_to_complete);      // Get whole hours (3)
    const minutes = Math.round((todoData.time_to_complete - hours) * 60);  // Get minutes (30)
    
    let timeStr = '';
    if (hours > 0) {
        timeStr = `${hours}h`;
        if (minutes > 0) {
            timeStr += ` ${minutes}m`;
        }
    } else {
        timeStr = `${minutes}m`;
    }
    document.getElementById('modalTimeToComplete').textContent = timeStr;
} else {
    document.getElementById('modalTimeToComplete').textContent = '-';
}
```

### Display Examples
- **0.5 hours** → Display: `30m`
- **1.0 hours** → Display: `1h`
- **1.5 hours** → Display: `1h 30m`
- **3.5 hours** → Display: `3h 30m`
- **24.75 hours** → Display: `24h 45m`
- **null** (no creation tracker) → Display: `-`

---

## Tracker Model

**File:** [app/models.py](app/models.py)

The `Tracker` model records every status change:

```python
class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.Text)
```

### When Tracker Records Are Created

1. **Status 5 (New):** When you create a todo
2. **Status 6 (Done):** When you click "Mark as Done"
3. **Status 7 (Failed):** If you mark as failed
4. **Status 8 (Re-assign):** If reassigned
5. **Status 9 (KIV):** If marked as "Keep In View"

---

## Data Flow

```
User Creates Todo
    ↓
Tracker record created (status_id=5, timestamp=2024-01-15 14:00:00)
    ↓
User works on todo...
    ↓
User clicks "Mark as Done"
    ↓
Tracker record created (status_id=6, timestamp=2024-01-15 17:30:00)
    ↓
Achievement modal calculates:
    time_diff = 17:30:00 - 14:00:00 = 3.5 hours
    ↓
Display: "Time Taken: 3h 30m"
```

---

## What If Time Taken is "-"?

If the modal shows `-` for Time Taken, it means:

1. **No creation tracker found** - The todo may have been created before the tracking system was implemented
2. **No completion tracker found** - The todo wasn't properly marked as done
3. **Data inconsistency** - System couldn't find both creation and completion timestamps

---

## Technical Details

### Timezone Consideration
- Timestamps are stored in UTC (`datetime.utcnow()`)
- The calculation uses UTC times, so the difference is accurate
- Display converts to user-friendly hours/minutes format

### Rounding
- Calculated in hours with 1 decimal place precision
- Example: `3.5` hours (3 hours 30 minutes)
- Minutes are calculated as: `(time_in_hours - whole_hours) * 60`
- Minutes are rounded to nearest integer

### Edge Cases
- **Same second completion:** Shows `0m`
- **Less than a minute:** Shows `0m` (rounds down)
- **Very old todos:** Accurately calculates even days-long durations
- **Todos not marked done:** Shows `-`

---

## Summary

The **Time Taken** calculation is:

✅ **Accurate** - Based on actual database timestamps
✅ **Automatic** - No manual entry needed
✅ **Real-time** - Updates immediately when you mark todo as done
✅ **User-friendly** - Displayed in human-readable format (hours and minutes)

It gives you insight into how much time you typically spend on tasks, helping you track productivity and estimate future todo durations.

