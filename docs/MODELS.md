# Database Models & Schema

**Last Updated:** January 16, 2026  
**Version:** 2.0

## Overview

TodoBox uses SQLAlchemy ORM with support for SQLite, MySQL, and PostgreSQL. All models are defined in `app/models.py` (26KB, 9 models).

## Database Schema

### Entity Relationship Diagram (Updated v2.0)

```bash
User (1) ───────────► (Many) Todo
  │                       │
  │                       ├──► (Many) Tracker (Status History)
  │                       │         └──► (1) Status
  │                       │
  │                       └──► (0..1) KIV (Keep In View)
  │
  ├──► (Many) ShareInvitation (Outgoing invitations)
  │
  ├──► (Many) TodoShare (As owner)
  │
  └──► (Many) TodoShare (As viewer)

DeletedAccount (Independent - Cooldown tracking)

TermsAndDisclaimer (Independent - Versioned terms)
```

## Model Summary

| Model | Purpose | Key Features |
|-------|---------|--------------|
| User | Authentication & account | OAuth, email verification, API tokens, timezone |
| Todo | Task management | Encrypted data, reminders, simple/advanced types |
| Status | Task statuses | 4 statuses: new, done, failed, re-assign |
| Tracker | Status history | Timestamp tracking, cascading delete |
| KIV | Keep In View | Separate KIV tracking, active/inactive |
| ShareInvitation | Sharing invites | Token-based, 7-day expiration |
| TodoShare | Sharing relationships | Owner-viewer pairs, unique constraint |
| DeletedAccount | Deletion cooldown | 7-day re-registration prevention |
| TermsAndDisclaimer | Terms versioning | Active/inactive versions |

## User Model

### Table: `user`

Stores user account information with support for both direct login and OAuth authentication.

### User Columns (Updated v2.0)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique user identifier |
| email | String(120) | UNIQUE, INDEX, NOT NULL | User email address (required) |
| fullname | String(100) | NULL | User's full name |
| password_hash | String(255) | NULL | Hashed password (NULL for OAuth users) |
| email_verified | Boolean | DEFAULT FALSE | Email verification status |
| api_token | String(255) | UNIQUE, INDEX | API token for REST API access |
| oauth_provider | String(50) | NULL | OAuth provider ('google' or NULL) |
| oauth_id | String(255) | INDEX | Google subject ID |
| sharing_enabled | Boolean | DEFAULT FALSE | Todo sharing feature toggle |
| is_admin | Boolean | DEFAULT FALSE | Admin user flag |
| is_blocked | Boolean | DEFAULT FALSE | Blocked user flag |
| timezone | String(50) | DEFAULT 'UTC' | User's timezone |
| created_at | DateTime | DEFAULT now() | Account creation timestamp |
| terms_accepted_version | String(50) | NULL | Accepted terms version |
| pending_deletion | Boolean | DEFAULT FALSE | Account marked for deletion |
| deletion_requested_at | DateTime | NULL | Deletion request timestamp |

### User Relationships

- `todo`: One-to-many relationship with Todo model
- `sent_invitations`: One-to-many with ShareInvitation (as sender)
- `shared_by_me`: One-to-many with TodoShare (as owner)
- `shared_with_me`: One-to-many with TodoShare (as viewer)

### User Methods

```python
User.seed()
```

Creates default admin user with email verification:
- Email: `admin@local.local`
- Password: `admin1234` (hashed)
- is_admin: True
- email_verified: True (auto-verified)

```python
set_password(password: str)
```

Hashes password using Werkzeug bcrypt and stores in `password_hash`

```python
check_password(password: str) -> bool
```

Verifies password against stored hash

```python
generate_api_token() -> str
```

Generates a new 32-character API token using `secrets.token_urlsafe()`

```python
check_api_token(token: str) -> bool
```

Validates provided API token against user's stored token

```python
get_user_by_api_token(token: str) -> User
```

Class method to retrieve user by API token

```python
check_email(email: str) -> bool
```

Checks if provided email matches user's email

```python
is_gmail_user() -> bool
```

Returns True if user authenticated via Google OAuth

```python
is_direct_login_user() -> bool
```

Returns True if user uses password authentication (not OAuth)

```python
can_share_todos() -> bool
```

Returns True if user has sharing enabled

```python
is_system_admin() -> bool
```

Returns True if user is an admin

### User Usage Example

```python
# Create direct login user
user = User(email='john@example.com', fullname='John Doe')
user.set_password('securepassword')
db.session.add(user)
db.session.commit()

# Create OAuth user (Google)
oauth_user = User(
    email='jane@gmail.com',
    oauth_provider='google',
    oauth_id='google_subject_id_123',
    fullname='Jane Smith'
)
oauth_user.email_verified = True  # OAuth users are auto-verified
db.session.add(oauth_user)
db.session.commit()

# Generate API token
token = user.generate_api_token()
print(f"API Token: {token}")

# Authenticate with password
user = User.query.filter_by(email='john@example.com').first()
if user and user.check_password('securepassword') and user.email_verified:
    # Login successful
    pass

# Authenticate with API token
user = User.get_user_by_api_token(token)
if user:
    # API authentication successful
    pass
```

## Todo Model

### Table: `todo`

Stores individual todo/task items with optional encryption and reminder support.

### Todo Columns (Updated v2.0)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique todo identifier |
| _name | Text | NOT NULL | **Encrypted** task title |
| _details | Text | NULL | **Encrypted** markdown description |
| _details_html | Text | NULL | **Encrypted** HTML-rendered description |
| timestamp | DateTime | INDEX, DEFAULT now() | Creation timestamp |
| modified | DateTime | INDEX, DEFAULT now() | Last modification timestamp |
| target_date | DateTime | INDEX, DEFAULT now() | Scheduled target date |
| reminder_enabled | Boolean | DEFAULT FALSE | Whether reminder is active |
| reminder_time | DateTime | NULL | When to send reminder notification |
| reminder_sent | Boolean | DEFAULT FALSE | Whether reminder has been sent |
| reminder_notification_count | Integer | DEFAULT 0 | Number of notifications sent |
| reminder_first_notification_time | DateTime | NULL | First notification timestamp |
| todo_type | String(20) | DEFAULT 'advanced' | 'simple' or 'advanced' |
| user_id | Integer | FOREIGN KEY(user.id) | Owner user reference |

**Note:** Fields prefixed with `_` are stored encrypted when `TODO_ENCRYPTION_ENABLED=True`. Access via properties `name`, `details`, `details_html` which automatically encrypt/decrypt.

### Todo Relationships

- `user`: Many-to-one relationship with User model
- `tracker_entries`: One-to-many with Tracker model
- **Implicit:** One-to-one with KIV model (via todo_id FK)

### Todo Properties (Encryption Support)

```python
@property
def name(self) -> str
    """Decrypt and return the todo name"""

@name.setter
def name(self, value: str)
    """Encrypt and store the todo name"""
```

Similar properties exist for `details` and `details_html`. When encryption is enabled, data is automatically encrypted on write and decrypted on read using Fernet symmetric encryption.

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
- Status not equal to 'done' (status_id != 6)
- Only latest tracker entry per todo

### Todo Instance Methods

```python
should_auto_close_reminder() -> bool
```

Checks if reminder should be auto-closed after 3 notifications within 30 minutes.

**Returns:** True if:
- 3 or more notifications sent
- All 3 within 30 minutes of first notification

### Todo String Representation

```python
def __repr__(self):
    return f'<Todo {self.name}>'
```

### Todo Usage Example

```python
# Create simple todo (checklist)
simple_todo = Todo(
    name='Shopping List',
    details='- [ ] Milk\n- [ ] Eggs\n- [ ] Bread',
    todo_type='simple',
    user_id=1
)
db.session.add(simple_todo)
db.session.commit()

# Create advanced todo with reminder
from datetime import datetime, timedelta

advanced_todo = Todo(
    name='Project Deadline',
    details='Complete the quarterly report',
    todo_type='advanced',
    reminder_enabled=True,
    reminder_time=datetime.now() + timedelta(hours=2),
    target_date=datetime.now() + timedelta(days=7),
    user_id=1
)
db.session.add(advanced_todo)
db.session.commit()

# Access encrypted fields (automatically decrypted)
print(advanced_todo.name)  # "Project Deadline" (decrypted)
print(advanced_todo.details)  # "Complete the quarterly report" (decrypted)

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

**Note:** Status IDs start from 5 by design in the seed method (`enumerate(statuses, start=5)`).

| ID | Name | Description |
|----|------|-------------|
| 5 | new | Newly created task |
| 6 | done | Completed task |
| 7 | failed | Failed task |
| 8 | re-assign | Reassigned task |
| 9 | kiv | Keep In View - tasks on hold |

### ⚠️ Pending Status Note

**Important:** There is currently NO explicit "pending" status_id in the Status table.

"Pending" is calculated as an **implicit state** in the dashboard:

- A todo is considered "pending" if it has NOT been marked as "done" (id=6) AND has NO re-assignment history
- This is derived state, not an actual database status

**See:** [REASSIGN_PENDING_LOGIC_ANALYSIS.md](REASSIGN_PENDING_LOGIC_ANALYSIS.md) for details on the potential logic gap and recommended solutions.

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
print(done_status.id)  # Output: 6
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

Deletes all tracker entries and the todo item itself. **Updated in v2.0** to handle KIV cascade deletion.

**Caution:** Permanently deletes the todo and all history

**Deletion Order (v2.0):**
1. Remove from KIV table (foreign key constraint)
2. Delete all Tracker entries
3. Delete the Todo record

**Example:**

```python
# Delete todo and its history (includes KIV)
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

---

## KIV Model (New in v2.0)

### Table: `KIV`

Separate table for Keep In View (KIV) todos, replacing the previous status-based approach.

### KIV Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique KIV entry |
| todo_id | Integer | FOREIGN KEY(todo.id), UNIQUE | Reference to todo (one-to-one) |
| user_id | Integer | FOREIGN KEY(user.id), INDEX | Owner reference |
| entered_at | DateTime | INDEX, DEFAULT now() | When marked as KIV |
| exited_at | DateTime | NULL | When removed from KIV |
| is_active | Boolean | INDEX, DEFAULT TRUE | Currently in KIV |

### KIV Static Methods

```python
KIV.add(todo_id: int, user_id: int)
```

Add a todo to KIV or reactivate if previously KIV.

```python
KIV.remove(todo_id: int)
```

Remove todo from KIV (marks as exited, keeps history).

```python
KIV.is_kiv(todo_id: int) -> bool
```

Check if todo is currently in KIV.

### KIV Usage Example

```python
# Mark todo as KIV
KIV.add(todo_id=5, user_id=1)

# Check if KIV
if KIV.is_kiv(todo_id=5):
    print("Todo is in KIV")

# Remove from KIV
KIV.remove(todo_id=5)
```

---

## ShareInvitation Model (New in v2.0)

### Table: `share_invitation`

Stores pending sharing invitations between users.

### ShareInvitation Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique invitation ID |
| from_user_id | Integer | FOREIGN KEY(user.id), NOT NULL | Sender user ID |
| to_email | String(120) | NOT NULL | Recipient email |
| token | String(64) | UNIQUE, INDEX, NOT NULL | Approval token |
| status | String(20) | DEFAULT 'pending' | pending/accepted/declined/expired |
| created_at | DateTime | DEFAULT now() | Creation timestamp |
| expires_at | DateTime | NOT NULL | Expiration timestamp (7 days) |
| responded_at | DateTime | NULL | Response timestamp |

### ShareInvitation Relationships

- `from_user`: Many-to-one with User (sender)

### ShareInvitation Methods

```python
is_expired() -> bool
```

Check if invitation has expired.

```python
is_pending() -> bool
```

Check if invitation is still pending and not expired.

```python
@property
display_status -> str
```

Get display status (handles expired pending invitations).

```python
@classmethod
get_by_token(token: str) -> ShareInvitation
```

Retrieve invitation by token.

### ShareInvitation Usage Example

```python
# Create invitation
invitation = ShareInvitation(
    from_user_id=1,
    to_email='friend@example.com',
    expires_in_days=7
)
db.session.add(invitation)
db.session.commit()

# Check status
if invitation.is_pending():
    print(f"Invitation token: {invitation.token}")

# Retrieve by token
inv = ShareInvitation.get_by_token(token)
if inv and inv.is_pending():
    inv.status = 'accepted'
    inv.responded_at = datetime.now()
    db.session.commit()
```

---

## TodoShare Model (New in v2.0)

### Table: `todo_share`

Tracks active todo sharing relationships between users.

### TodoShare Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique share relationship |
| owner_id | Integer | FOREIGN KEY(user.id), NOT NULL | Todo owner |
| shared_with_id | Integer | FOREIGN KEY(user.id), NOT NULL | Viewer |
| created_at | DateTime | DEFAULT now() | Share creation time |

**Unique Constraint:** `(owner_id, shared_with_id)` - Each pair can only share once

### TodoShare Relationships

- `owner`: Many-to-one with User (owner)
- `shared_with`: Many-to-one with User (viewer)

### TodoShare Static Methods

```python
@classmethod
get_shared_users(user_id: int) -> List[User]
```

Get users who have shared their todos with this user.

```python
@classmethod
get_users_i_share_with(user_id: int) -> List[User]
```

Get users this user shares their todos with.

```python
@classmethod
is_sharing_with(owner_id: int, shared_with_id: int) -> bool
```

Check if owner is sharing with the specified user.

### TodoShare Usage Example

```python
# Create sharing relationship
share = TodoShare(owner_id=1, shared_with_id=2)
db.session.add(share)
db.session.commit()

# Check if sharing
if TodoShare.is_sharing_with(owner_id=1, shared_with_id=2):
    print("User 1 is sharing with User 2")

# Get all users sharing with me
shared_users = TodoShare.get_shared_users(user_id=2)
for user in shared_users:
    print(f"Viewing todos from: {user.email}")
```

---

## DeletedAccount Model (New in v2.0)

### Table: `deleted_account`

Tracks deleted accounts with 7-day cooldown to prevent immediate re-registration.

### DeletedAccount Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique entry |
| email | String(120) | INDEX | Deleted account email |
| oauth_id | String(255) | INDEX, NULL | OAuth ID (for OAuth users) |
| deleted_at | DateTime | DEFAULT now() | Deletion timestamp |
| cooldown_until | DateTime | NOT NULL | Re-registration allowed after |

### DeletedAccount Usage Example

```python
from datetime import datetime, timedelta

# Record account deletion
deleted = DeletedAccount(
    email='user@example.com',
    oauth_id='google_123',  # NULL for direct login users
    deleted_at=datetime.now(),
    cooldown_until=datetime.now() + timedelta(days=7)
)
db.session.add(deleted)
db.session.commit()

# Check if email is in cooldown
cooldown = DeletedAccount.query.filter_by(email='user@example.com').filter(
    DeletedAccount.cooldown_until > datetime.now()
).first()

if cooldown:
    print(f"Account in cooldown until {cooldown.cooldown_until}")
```

---

## TermsAndDisclaimer Model (New in v2.0)

### Table: `terms_and_disclaimer`

Versioned terms of service and disclaimer management.

### TermsAndDisclaimer Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique version ID |
| version | String(50) | NOT NULL | Version identifier |
| content | Text | NOT NULL | Terms HTML content |
| is_active | Boolean | DEFAULT TRUE | Active version flag |
| created_at | DateTime | DEFAULT now() | Creation timestamp |

### TermsAndDisclaimer Static Methods

```python
@classmethod
get_active_terms() -> TermsAndDisclaimer
```

Get the currently active terms version.

### TermsAndDisclaimer Usage Example

```python
# Create new terms version
terms = TermsAndDisclaimer(
    version='1.1',
    content='<h1>Terms of Service</h1><p>...</p>',
    is_active=True
)
db.session.add(terms)

# Deactivate old version
old_terms = TermsAndDisclaimer.query.filter_by(version='1.0').first()
if old_terms:
    old_terms.is_active = False

db.session.commit()

# Get active terms
active_terms = TermsAndDisclaimer.get_active_terms()
print(f"Current version: {active_terms.version}")
```

---

## Database Migrations

All schema changes are managed via Alembic migrations in `migrations/versions/`.

**Key Migrations:**
- User model: OAuth support, email verification, API tokens
- Todo model: Encryption fields, reminder system, todo types
- KIV table: Separate KIV tracking
- ShareInvitation/TodoShare: Sharing feature
- DeletedAccount: Cooldown system
- TermsAndDisclaimer: Terms versioning

**Run migrations:**

```bash
flask db upgrade
```

---

## Best Practices

### Data Encryption

Enable encryption in `.flaskenv`:

```bash
TODO_ENCRYPTION_ENABLED=True
```

Ensure `SECRET_KEY` and `SALT` are set securely.

### User Ownership

Always verify user ownership before operations:

```python
todo = Todo.query.get(todo_id)
if todo.user_id != current_user.id:
    abort(403)  # Forbidden
```

### Reminder Auto-Close

Reminders auto-close after 3 notifications within 30 minutes to prevent fatigue.

### Sharing Permissions

Only Gmail users (OAuth) can enable sharing:

```python
if current_user.is_gmail_user():
    current_user.sharing_enabled = True
```
