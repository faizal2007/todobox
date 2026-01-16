# Achievement Modal - Time Taken Calculation

## What is "Time Taken"?

The **"Time Taken"** field in the achievement modal shows **how long you actually worked** on a todo from when you clicked "Start Work" until you marked it as done.

---

## How It's Calculated (Updated Method)

### Status IDs (Key to Understanding)

The system tracks todo status with these IDs:
- **Status ID 5:** "New" - when todo is created (NOT used for time calculation)
- **Status ID 6:** "Done" - when todo is marked as complete
- **Status ID 10:** "Started" - when user clicks "Start Work" button ← **USED FOR TIME CALCULATION**
- **Status ID 11:** "Paused" - when work session is paused
- **Status ID 12:** "Resumed" - when work session is resumed

### The Calculation Formula (Current - Accurate)

```
Time Taken = Timestamp(Done) - Timestamp(First Start)
           = When marked done - When first clicked "Start Work"
           = Reflects actual work time spent, not planning time
           = Displayed as: seconds → minutes → hours → days → years
```

### Code Location

**File:** [app/routes.py](app/routes.py#L2005-L2014)

```python
# Get the first 'started' tracker (when user began working)
started_tracker = Tracker.query.filter_by(
    todo_id=todo_id,
    status_id=10  # Started - actual work begins here
).order_by(Tracker.timestamp.asc()).first()

# Get the completion tracker (when todo was marked done)
completion_tracker = Tracker.query.filter_by(
    todo_id=todo_id,
    status_id=6  # "Done" status - when completed
).order_by(Tracker.timestamp.desc()).first()

# Calculate the difference in hours
time_to_complete = None
if started_tracker and completion_tracker:
    # Calculate total work time from when work started to when completed
    time_diff = completion_tracker.timestamp - started_tracker.timestamp
    time_to_complete = round(time_diff.total_seconds() / 3600, 1)
```

---

## Example Calculation

### Scenario
- **Created:** January 15, 2024 at 2:00 PM
- **Clicked "Start Work":** January 15, 2024 at 5:00 PM (after rescheduling 3 times)
- **Marked Done:** January 15, 2024 at 5:30 PM

### Math
```
Time Difference = 5:30 PM - 5:00 PM  (From Start, NOT from creation)
                = 30 minutes
                = 0.5 hours
                
In seconds: 0.5 * 3600 = 1,800 seconds
Rounded to 1 decimal: 0.5 hours
```

### Display in Modal
```
Time Taken: 30m
```

**Why this is better:**
- Old method: Would show 3.5 hours (2 PM → 5:30 PM including planning time)
- **New method: Shows 30 minutes (actual work time)**


---

## How It's Displayed in the Modal

**File:** [app/templates/achievements.html](app/templates/achievements.html#L628-L665)

```javascript
// NEW METHOD: Shows seconds, minutes, hours, days, years progressively
if (todoData.time_to_complete !== null && todoData.time_to_complete !== undefined) {
    const totalSeconds = todoData.time_to_complete * 3600;  // Convert hours to seconds
    const seconds = Math.round(totalSeconds % 60);
    const minutes = Math.floor((totalSeconds / 60) % 60);
    const hours = Math.floor((totalSeconds / 3600) % 24);
    const days = Math.floor((totalSeconds / 86400) % 365);
    const years = Math.floor(totalSeconds / (86400 * 365));
    
    // Display progressively: 45s, 5m 30s, 2h 15m, 3d 5h, 1y 2d
    if (years > 0) {
        timeStr = `${years}y`;
        if (days > 0) timeStr += ` ${days}d`;
    } else if (days > 0) {
        timeStr = `${days}d`;
        if (hours > 0) timeStr += ` ${hours}h`;
    } else if (hours > 0) {
        timeStr = `${hours}h`;
        if (minutes > 0) timeStr += ` ${minutes}m`;
    } else if (minutes > 0) {
        timeStr = `${minutes}m`;
        if (seconds > 0) timeStr += ` ${seconds}s`;
    } else {
        timeStr = `${seconds}s`;
    }
    document.getElementById('modalTimeToComplete').textContent = timeStr;
}
```

### Display Examples (NEW WITH SECONDS)
- **30 seconds** → Display: `30s`
- **2 minutes 15 seconds** → Display: `2m 15s`
- **1 hour 30 minutes** → Display: `1h 30m`
- **3 hours 45 minutes** → Display: `3h 45m`
- **1 day 5 hours** → Display: `1d 5h`
- **7 days 2 hours** → Display: `7d 2h`
- **1 year 45 days** → Display: `1y 45d`
- **null** (no work started) → Display: `-`


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

