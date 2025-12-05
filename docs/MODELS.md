# Database Models & Schema

## Overview

TodoBox uses SQLAlchemy ORM with support for SQLite, MySQL, and PostgreSQL. All models are defined in `app/models.py`.

## Database Schema

### Entity Relationship Diagram

```text
User (1) -----> (Many) Todo
                    |
                    v
                Tracker (junction table)
                    |
                    v
                Status
```

## User Model

### Table: `user`

Stores user account information and authentication credentials.

### User Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique user identifier |
| username | String(64) | UNIQUE, INDEX | User login username |
| email | String(120) | UNIQUE, INDEX | User email address |
| fullname | String(100) | NULL | User's full name |
| password_hash | String(128) | NULL | Hashed password (bcrypt) |

### User Relationships

- `todo`: One-to-many relationship with Todo model

### User Methods

```python
User.seed()
```

Creates default admin user:

- Username: `admin`
- Email: `admin@examples.com`
- Password: `admin1234` (hashed)

```python
set_password(password: str)
```

Hashes password using Werkzeug and stores in `password_hash`

```python
check_password(password: str) -> bool
```

Verifies password against stored hash

```python
check_username(username: str) -> bool
```

Checks if provided username matches user's username

```python
check_email(email: str) -> bool
```

Checks if provided email matches user's email

### User Usage Example

```python
# Create user
user = User(username='john', email='john@example.com')
user.set_password('securepassword')
db.session.add(user)
db.session.commit()

# Authenticate
user = User.query.filter_by(username='john').first()
if user and user.check_password('securepassword'):
    # Login successful
    pass
```

## Todo Model

### Table: `todo`

Stores individual todo/task items.

### Todo Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique todo identifier |
| name | String(80) | NOT NULL, INDEX | Task title |
| details | String(250) | NULL | Markdown task description |
| details_html | String(500) | NULL | HTML-rendered description |
| timestamp | DateTime | INDEX, DEFAULT(now) | Creation timestamp |
| modified | DateTime | INDEX, DEFAULT(now) | Last modification timestamp |
| user_id | Integer | FOREIGN KEY(user.id) | Owner user reference |

### Todo Relationships

- `user`: Many-to-one relationship with User model
- `tracker`: Many-to-many relationship with Status model via Tracker junction table

### Todo Static Methods

```python
Todo.getList(type: str, start: str, end: str) -> Query
```

Retrieves todo items for specified date range.

**Parameters:**

- `type`: Filter type (e.g., 'today', 'tomorrow')
- `start`: Start datetime string (e.g., '2024-01-15 00:00')
- `end`: End datetime string (e.g., '2024-01-15 23:59')

**Returns:** Query object filtered by:

- Timestamp between start and end
- Status not equal to 'done' (status_id != 2)
- Only latest tracker entry per todo

### Todo String Representation

```python
def __repr__(self):
    return f'<Todo {self.name}'
```

### Todo Usage Example

```python
# Create todo
todo = Todo(
    name='Complete project',
    details='Finish coding and testing',
    details_html='<p>Finish coding and testing</p>',
    user_id=1
)
db.session.add(todo)
db.session.commit()

# Query todos
user_todos = Todo.query.filter_by(user_id=1).all()
today_todos = Todo.getList('today', start, end)
```

## Status Model

### Table: `status`

Defines todo item status types.

### Status Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique status identifier |
| name | String(50) | NOT NULL, INDEX | Status name |

### Default Status Types

| ID | Name | Description |
|----|------|-------------|
| 5 | new | Newly created task |
| 6 | done | Completed task |
| 7 | failed | Failed task |
| 8 | re-assign | Reassigned task |
| 9 | kiv | Keep In View - tasks on hold |

### Status Methods

```python
Status.seed()
```

Populates the status table with default status types.

### Status String Representation

```python
def __repr__(self):
    return f'<Todo {self.name}'
```

### Status Usage Example

```python
# Seed default statuses
Status.seed()

# Query specific status
done_status = Status.query.filter_by(name='done').first()
print(done_status.id)  # Output: 2
```

## Tracker Model

### Table: `tracker` (Junction Table)

Many-to-many relationship table tracking todo status changes over time.

### Tracker Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique tracker entry |
| todo_id | Integer | FOREIGN KEY(todo.id) | Reference to todo item |
| status_id | Integer | FOREIGN KEY(status.id) | Reference to status |
| timestamp | DateTime | INDEX, DEFAULT(now) | When status changed |

### Tracker Attributes

```python
class Tracker(object):
    def __init__(self, todo_id, status_id, timestamp=datetime.now())
```

### Tracker Static Methods

```python
Tracker.add(todo_id: int, status_id: int, timestamp=datetime.now())
```

Creates new tracker entry and commits to database.

**Example:**

```python
# Mark todo as done
Tracker.add(todo_id=1, status_id=2, timestamp=datetime.now())
```

```python
Tracker.getId(todo_id: int) -> int
```

Gets the tracker ID for the latest status change of a todo item.

**Returns:** Tracker ID of most recent entry

```python
Tracker.delete(todo_id: int)
```

Deletes all tracker entries and the todo item itself.

**Caution:** Permanently deletes the todo and all history

**Example:**

```python
# Delete todo and its history
Tracker.delete(todo_id=1)
```

### Tracker Usage Example

```python
# Create tracker entry for new todo
todo = Todo(name='New Task', user_id=1)
db.session.add(todo)
db.session.commit()
Tracker.add(todo.id, 1, datetime.now())  # Status: new

# Later, mark as done
Tracker.add(todo.id, 2, datetime.now())  # Status: done

# Get latest status change
latest_id = Tracker.getId(todo.id)
```

## Foreign Key Relationships

### User → Todo (One-to-Many)

- A user can have many todo items
- Each todo belongs to exactly one user
- Foreign Key: `todo.user_id → user.id`

### Todo → Status (Many-to-Many via Tracker)

- A todo can have multiple status changes
- Each status can be applied to many todos
- Junction Table: `tracker`

## Indexes

The following columns are indexed for query performance:

- `user.username`
- `user.email`
- `todo.name`
- `todo.timestamp`
- `todo.modified`
- `status.name`
- `tracker.timestamp`

## Constraints

| Constraint | Type | Description |
|-----------|------|-------------|
| UNIQUE(user.username) | Unique | No duplicate usernames |
| UNIQUE(user.email) | Unique | No duplicate emails |
| NOT NULL(todo.name) | Check | Todo title required |
| FK(todo.user_id) | Foreign Key | Todo must belong to user |
| FK(tracker.todo_id) | Foreign Key | Tracker must reference todo |
| FK(tracker.status_id) | Foreign Key | Tracker must reference status |

## Database Initialization

### SQLite

```python
# Automatic creation in instance directory
instance/todobox.db
```

### MySQL/PostgreSQL

```bash
flask db upgrade
```

This runs Alembic migrations to create tables and indexes.

## Data Integrity

### Cascading Deletes

When a user is deleted:

- All associated todo items are NOT automatically deleted
- Must manually delete todos first

When a todo is deleted via `Tracker.delete()`:

- All tracker entries are deleted
- The todo item is deleted

## Query Examples

### Get All Todos for User

```python
user = User.query.get(1)
todos = user.todo.all()
```

### Get Today's Pending Tasks

```python
from datetime import date
query_date = date.today()
start = f'{query_date} 00:00'
end = f'{query_date} 23:59'
todos = Todo.getList('today', start, end).order_by(Todo.timestamp.desc()).all()
```

### Get Completed Tasks

```python
completed = Todo.query.filter(Todo.tracker.any(Status.name == 'done')).all()
```

### Count User's Todos

```python
user_id = 1
count = Todo.query.filter_by(user_id=user_id).count()
```

### Get Todo Status History

```python
from app import db
history = db.session.query(Tracker, Status).join(Status).filter(
    Tracker.todo_id == 1
).order_by(Tracker.timestamp.desc()).all()
```
