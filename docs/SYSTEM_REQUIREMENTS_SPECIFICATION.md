# System Requirements Specification (SRS)
## TodoBox Application - Complete Feature Set

**Document Version:** 1.0  
**Date:** January 16, 2026  
**Last Updated:** January 16, 2026  
**Status:** CURRENT & ACTIVE

---

## 1. Executive Summary

TodoBox is a comprehensive task management and time tracking application built with Flask. It enables users to:
- Create, manage, and track todos across multiple views (Today, Tomorrow, Later)
- Measure actual time spent on work (not planning time)
- Achieve structured goals through a checklist system
- Monitor achievements and productivity
- Integrate third-party services (OAuth, Email, Geolocation, Timezone)

**Key Innovation:** Accurate time tracking using "Start Work" status, excluding planning and rescheduling time from calculations.

---

## 2. Functional Requirements

### 2.1 User Authentication & Authorization

#### 2.1.1 User Registration
- **REQ-AUTH-001:** System shall allow new users to register with email and password
- **REQ-AUTH-002:** Password must be at least 8 characters with mixed case and numbers
- **REQ-AUTH-003:** Email verification required before account activation
- **REQ-AUTH-004:** Passwords stored with bcrypt hashing (never plain text)
- **REQ-AUTH-005:** Duplicate email registration prevented

#### 2.1.2 User Login
- **REQ-AUTH-006:** Users may login with registered email and password
- **REQ-AUTH-007:** Login failures recorded for security audit
- **REQ-AUTH-008:** Session timeout after 30 days of inactivity
- **REQ-AUTH-009:** "Remember me" option for persistent login
- **REQ-AUTH-010:** Logout clears all session data

#### 2.1.3 OAuth Integration
- **REQ-AUTH-011:** Google OAuth 2.0 support for one-click login
- **REQ-AUTH-012:** OAuth tokens stored securely (not in plain text)
- **REQ-AUTH-013:** User can link/unlink OAuth accounts from settings
- **REQ-AUTH-014:** OAuth profile data synced with user account

#### 2.1.4 Password Reset
- **REQ-AUTH-015:** Users can request password reset via email
- **REQ-AUTH-016:** Reset link valid for 1 hour only
- **REQ-AUTH-017:** Reset link one-time use only

---

### 2.2 Todo Management

#### 2.2.1 Todo Creation
- **REQ-TODO-001:** Users can create new todos with title and optional description
- **REQ-TODO-002:** Each todo has a `target_date` (when it should be done)
- **REQ-TODO-003:** Target date selector with calendar UI
- **REQ-TODO-004:** Default target_date is "Today"
- **REQ-TODO-005:** Todos can be created in bulk (comma-separated)

#### 2.2.2 Todo Views
- **REQ-TODO-006:** `/today` view shows todos due today
- **REQ-TODO-007:** `/tomorrow` view shows todos due tomorrow  
- **REQ-TODO-008:** `/later` view shows todos due in 7+ days
- **REQ-TODO-009:** Todos organized by date in chronological order
- **REQ-TODO-010:** Search functionality across all todos
- **REQ-TODO-011:** Filter by status (New, Done, Failed, KIV)

#### 2.2.3 Todo Editing
- **REQ-TODO-012:** Users can edit todo title and description
- **REQ-TODO-013:** Users can change target_date (reschedule)
- **REQ-TODO-014:** Reschedule creates Status 8 (Re-assign) tracker record
- **REQ-TODO-015:** Edit history not stored (one-way edits)

#### 2.2.4 Todo Status Management
- **REQ-TODO-016:** Todos have 5 main statuses: New, Done, Failed, KIV, Started
- **REQ-TODO-017:** User can mark todo as "Done"
- **REQ-TODO-018:** User can mark todo as "Failed"
- **REQ-TODO-019:** User can mark todo as "KIV" (Keep In View - paused)
- **REQ-TODO-020:** User can click "Start Work" to begin time tracking
- **REQ-TODO-021:** Once done, cannot revert to earlier status (one-way state machine)

#### 2.2.5 Todo Deletion
- **REQ-TODO-022:** Soft delete only - todos marked as deleted, not removed from DB
- **REQ-TODO-023:** Deleted todos hidden from all views by default
- **REQ-TODO-024:** Admin can view deleted todos in special view

---

### 2.3 Work Session Tracking (Accurate Time Measurement)

#### 2.3.1 Start Work Feature
- **REQ-TIME-001:** Each todo has "Start Work" button (play icon)
- **REQ-TIME-002:** Clicking opens modal with timer display (HH:MM:SS)
- **REQ-TIME-003:** Start button begins counting elapsed time
- **REQ-TIME-004:** Modal tracks elapsed seconds in browser memory
- **REQ-TIME-005:** Only one active work session allowed system-wide

#### 2.3.2 Work Session Pause/Resume
- **REQ-TIME-006:** Pause button stops timer without closing modal
- **REQ-TIME-007:** Resume button continues from paused elapsed time
- **REQ-TIME-008:** Elapsed time preserved when modal closed
- **REQ-TIME-009:** Reopening modal shows Start button with previous elapsed time
- **REQ-TIME-010:** Auto-pause previous session when starting new todo's session

#### 2.3.3 Work Session End
- **REQ-TIME-011:** End button marks todo as "Done" and closes modal
- **REQ-TIME-012:** Closing modal without End button auto-pauses (state preserved)
- **REQ-TIME-013:** Session state persists across page refreshes

#### 2.3.4 Time Calculation (Status-Based)
- **REQ-TIME-014:** Time Taken = Timestamp(Done) - Timestamp(Start Work)
- **REQ-TIME-015:** Time calculated from Status 10 (Started), NOT Status 5 (Created)
- **REQ-TIME-016:** Reschedules (Status 8) DO NOT affect time calculation
- **REQ-TIME-017:** Multiple reschedules RESET timer (only last session counts)
- **REQ-TIME-018:** Todos without Status 10 (never started) show "-" for time taken

#### 2.3.5 Time Display Format
- **REQ-TIME-019:** Time displayed with progressive units: seconds → minutes → hours → days → years
- **REQ-TIME-020:** Display examples: `30s`, `5m 15s`, `2h 30m`, `3d 5h`, `1y 2d`
- **REQ-TIME-021:** Rounding to nearest whole unit (no decimals)

---

### 2.4 Achievements & Milestones

#### 2.4.1 Achievement Modal
- **REQ-ACH-001:** Modal displays on todo completion with celebration UI
- **REQ-ACH-002:** Shows: Todo title, completion time, date completed
- **REQ-ACH-003:** Shows "Time Taken" in user-friendly format
- **REQ-ACH-004:** Displays progress toward daily/weekly goals

#### 2.4.2 Milestone Tracking
- **REQ-ACH-005:** Track todos completed: 10, 25, 50, 100, 250, 500, 1000
- **REQ-ACH-006:** Milestone notifications on achievement
- **REQ-ACH-007:** Milestone badges shown on profile

#### 2.4.3 Statistics Dashboard
- **REQ-ACH-008:** Track total todos created
- **REQ-ACH-009:** Track total todos completed
- **REQ-ACH-010:** Track completion percentage
- **REQ-ACH-011:** Track average time per todo
- **REQ-ACH-012:** Show daily/weekly completion charts

---

### 2.5 Checklist Items (Sub-tasks)

#### 2.5.1 Checklist CRUD
- **REQ-CHKLIST-001:** Todos can have multiple checkbox items
- **REQ-CHKLIST-002:** Users can add, edit, delete checklist items
- **REQ-CHKLIST-003:** Checklist items can be marked complete/incomplete
- **REQ-CHKLIST-004:** Strikethrough text on completed items
- **REQ-CHKLIST-005:** Checklist progress shown as percentage

#### 2.5.2 Checklist Display
- **REQ-CHKLIST-006:** Checklist items rendered as interactive HTML checkboxes
- **REQ-CHKLIST-007:** Inline editing of checklist items
- **REQ-CHKLIST-008:** Keyboard shortcut (Tab + Spacebar) to toggle checkboxes

---

### 2.6 Reminders & Notifications

#### 2.6.1 Email Reminders
- **REQ-REMIND-001:** Users can set email reminders for todos
- **REQ-REMIND-002:** Reminder times: At assignment, 1 hour before, 1 day before
- **REQ-REMIND-003:** Reminders sent via SMTP
- **REQ-REMIND-004:** Reminders auto-close when todo completed
- **REQ-REMIND-005:** Reminder opt-out available in settings

#### 2.6.2 In-App Notifications
- **REQ-REMIND-006:** Toast notifications for status changes
- **REQ-REMIND-007:** Notification center stores last 30 days of notifications
- **REQ-REMIND-008:** Mark notifications as read

---

### 2.7 Timezone Support

#### 2.7.1 Timezone Detection
- **REQ-TZ-001:** Auto-detect user timezone from browser geolocation
- **REQ-TZ-002:** Manual timezone selection in settings
- **REQ-TZ-003:** Support all IANA timezone identifiers
- **REQ-TZ-004:** All timestamps stored in UTC, displayed in user's timezone

#### 2.7.2 Timezone Features
- **REQ-TZ-005:** "Today" definition uses user's local midnight
- **REQ-TZ-006:** Reminders sent at correct user local time
- **REQ-TZ-007:** Daylight saving time handled automatically

---

### 2.8 User Profile & Settings

#### 2.8.1 Profile Management
- **REQ-PROFILE-001:** Users can view their profile with avatar
- **REQ-PROFILE-002:** Users can update profile picture
- **REQ-PROFILE-003:** Users can set display name
- **REQ-PROFILE-004:** Users can set bio/about section

#### 2.8.2 Settings
- **REQ-PROFILE-005:** Users can change email address
- **REQ-PROFILE-006:** Users can change password
- **REQ-PROFILE-007:** Users can enable/disable email reminders
- **REQ-PROFILE-008:** Users can choose light/dark theme
- **REQ-PROFILE-009:** Users can export their data (JSON/CSV)
- **REQ-PROFILE-010:** Users can delete their account (soft delete)

---

### 2.9 Admin Features

#### 2.9.1 User Management
- **REQ-ADMIN-001:** Admins can view all users
- **REQ-ADMIN-002:** Admins can disable/enable user accounts
- **REQ-ADMIN-003:** Admins can view user activity logs
- **REQ-ADMIN-004:** Admins can export user data

#### 2.9.2 System Monitoring
- **REQ-ADMIN-005:** View system statistics (total users, todos, active sessions)
- **REQ-ADMIN-006:** View error logs
- **REQ-ADMIN-007:** Manual trigger for reminder jobs

---

## 3. Non-Functional Requirements

### 3.1 Performance

#### 3.1.1 Response Time
- **REQ-PERF-001:** Page load time < 2 seconds on 4G network
- **REQ-PERF-002:** API endpoints respond in < 500ms for 99th percentile
- **REQ-PERF-003:** Modal open in < 100ms
- **REQ-PERF-004:** Search results in < 1 second for up to 10,000 todos

#### 3.1.2 Scalability
- **REQ-PERF-005:** Support 10,000 concurrent users
- **REQ-PERF-006:** Database handles 100,000,000+ todo records
- **REQ-PERF-007:** Cache hot data (user profiles, settings)

#### 3.1.3 Resource Usage
- **REQ-PERF-008:** JavaScript bundle < 500KB gzipped
- **REQ-PERF-009:** Memory per session < 5MB

### 3.2 Security

#### 3.2.1 Authentication
- **REQ-SEC-001:** All passwords hashed with bcrypt (salt rounds: 10)
- **REQ-SEC-002:** Session tokens stored as secure HTTP-only cookies
- **REQ-SEC-003:** CSRF protection on all state-changing endpoints
- **REQ-SEC-004:** OAuth tokens encrypted at rest

#### 3.2.2 Authorization
- **REQ-SEC-005:** Users can only access their own todos
- **REQ-SEC-006:** Users cannot modify other users' todos
- **REQ-SEC-007:** Admins have elevated permissions logged

#### 3.2.3 Data Protection
- **REQ-SEC-008:** All API endpoints require authentication (except login/register)
- **REQ-SEC-009:** Sensitive data (passwords, tokens) never logged
- **REQ-SEC-010:** Input sanitization on all user inputs
- **REQ-SEC-011:** SQL injection prevention (parameterized queries)
- **REQ-SEC-012:** XSS prevention (HTML escaping, Content Security Policy)
- **REQ-SEC-013:** HTTPS enforced (301 redirect from HTTP)

#### 3.2.4 Compliance
- **REQ-SEC-014:** GDPR compliant (user data export/deletion)
- **REQ-SEC-015:** CCPA compliant
- **REQ-SEC-016:** PCI DSS (if payment processing added)

### 3.3 Reliability

#### 3.3.1 Availability
- **REQ-REL-001:** 99.9% uptime SLA
- **REQ-REL-002:** Graceful degradation if database unavailable
- **REQ-REL-003:** Offline mode caches recent data

#### 3.3.2 Data Integrity
- **REQ-REL-004:** Database backups daily
- **REQ-REL-005:** Backup retention: 30 days
- **REQ-REL-006:** Transaction ACID compliance for todo updates
- **REQ-REL-007:** No data loss on session timeout

#### 3.3.3 Error Handling
- **REQ-REL-008:** Graceful error messages for users
- **REQ-REL-009:** Error tracking with Sentry/similar
- **REQ-REL-010:** Automatic error notifications to ops team

### 3.4 Usability

#### 3.4.1 Interface Design
- **REQ-USAB-001:** Mobile responsive (works on 320px+ screens)
- **REQ-USAB-002:** Keyboard navigation support
- **REQ-USAB-003:** WCAG 2.1 AA accessibility compliance
- **REQ-USAB-004:** Dark/light theme toggle

#### 3.4.2 User Experience
- **REQ-USAB-005:** Onboarding tutorial on first login
- **REQ-USAB-006:** Undo/redo for todo actions
- **REQ-USAB-007:** Drag-and-drop to reorder todos
- **REQ-USAB-008:** Quick add todo with keyboard shortcut (Ctrl+N)

### 3.5 Maintainability

#### 3.5.1 Code Quality
- **REQ-MAINT-001:** Python code follows PEP 8
- **REQ-MAINT-002:** JavaScript/jQuery code follows consistent style
- **REQ-MAINT-003:** Test coverage > 80%
- **REQ-MAINT-004:** Code review required for all PRs

#### 3.5.2 Documentation
- **REQ-MAINT-005:** API documentation with Swagger/OpenAPI
- **REQ-MAINT-006:** Architecture decision records (ADRs)
- **REQ-MAINT-007:** Deployment runbook
- **REQ-MAINT-008:** Troubleshooting guide

#### 3.5.3 Logging & Monitoring
- **REQ-MAINT-009:** All errors logged with timestamp and context
- **REQ-MAINT-010:** Performance metrics tracked (response times, DB queries)
- **REQ-MAINT-011:** Security events logged (login attempts, permission changes)

---

## 4. System Architecture

### 4.1 Technology Stack

**Backend:**
- Python 3.9+ with Flask
- MySQL 8.0+ database
- SQLAlchemy ORM
- Alembic for migrations
- Gunicorn WSGI server

**Frontend:**
- HTML5/CSS3
- Bootstrap 4.5+
- jQuery 3.5+
- JavaScript ES6

**External Services:**
- SMTP for email (Gmail, SendGrid)
- Google OAuth 2.0
- Geolocation API
- Timezone database

**DevOps:**
- Git for version control
- Docker for containerization
- GitHub Actions for CI/CD
- MySQL for production database

### 4.2 Database Schema

**Core Tables:**
- `user` - User accounts
- `todo` - Todo items
- `checklist_item` - Sub-tasks
- `tracker` - Status change history
- `status` - Status reference data
- `reminder` - Scheduled reminders
- `notification` - User notifications

**Status IDs (Tracker):**
- `5` - New
- `6` - Done
- `7` - Failed
- `8` - Re-assign (rescheduled)
- `9` - KIV (Keep In View)
- `10` - Started (work session began)
- `11` - Paused (work session paused)
- `12` - Resumed (work session resumed)

### 4.3 API Endpoints

**Authentication:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirm

**Todo Operations:**
- `GET /{path:date}` - List todos for date (today/tomorrow/later)
- `POST /todo/create` - Create new todo
- `POST /<id>/edit` - Update todo
- `POST /<id>/delete` - Soft delete todo
- `GET /api/todo/<id>/details` - Get todo details with time taken

**Work Session:**
- `POST /<id>/start` - Begin work session (Status 10)
- `POST /<id>/pause` - Pause work session (Status 11)
- `POST /<id>/resume` - Resume work session (Status 12)
- `POST /<id>/done` - Complete todo (Status 6)

**Achievements:**
- `GET /achievements` - Achievement modal data
- `GET /api/achievements/batch` - Batch fetch achievements

**Settings:**
- `GET /settings` - User settings page
- `POST /settings/update` - Update settings

---

## 5. Data Requirements

### 5.1 Data Storage
- **REQ-DATA-001:** All user data stored in MySQL
- **REQ-DATA-002:** No user data stored in browser localStorage (except CSRF token)
- **REQ-DATA-003:** Session data stored on server (Flask sessions)

### 5.2 Data Retention
- **REQ-DATA-004:** Todo data retained for 7 years (compliance)
- **REQ-DATA-005:** Deleted todos in trash for 30 days before permanent delete
- **REQ-DATA-006:** Logs retained for 90 days

### 5.3 Data Privacy
- **REQ-DATA-007:** Users can export their data
- **REQ-DATA-008:** Users can delete their account
- **REQ-DATA-009:** No third-party data sharing
- **REQ-DATA-010:** Encryption at rest for sensitive fields

---

## 6. Integration Requirements

### 6.1 External Services
- **Google OAuth** - One-click login
- **SMTP** - Email delivery
- **Geolocation** - Timezone detection
- **IANA Timezone Database** - Timezone support

### 6.2 APIs
- **REQ-INT-001:** RESTful API design with JSON
- **REQ-INT-002:** Pagination support (limit, offset)
- **REQ-INT-003:** Error responses in standard format
- **REQ-INT-004:** CORS enabled for authorized domains

---

## 7. Deployment Requirements

### 7.1 Environments
- **Development:** Local machine with SQLite or MySQL
- **Staging:** Cloud instance with MySQL, staging OAuth
- **Production:** Load-balanced servers with RDS MySQL

### 7.2 Deployment Process
- **REQ-DEPLOY-001:** Blue-green deployment strategy
- **REQ-DEPLOY-002:** Zero-downtime migrations
- **REQ-DEPLOY-003:** Automated backups before deployment
- **REQ-DEPLOY-004:** Rollback capability within 5 minutes

---

## 8. Acceptance Criteria

### 8.1 Functional Testing
- ✅ All user workflows tested (create → start → complete)
- ✅ Time calculation accurate across reschedules
- ✅ Achievement modal displays correctly
- ✅ Email reminders sent on schedule
- ✅ OAuth login works end-to-end

### 8.2 Non-Functional Testing
- ✅ Load testing: 1000 concurrent users
- ✅ Security testing: OWASP Top 10 covered
- ✅ Accessibility: WCAG 2.1 AA compliance
- ✅ Performance: 99th percentile response < 500ms

### 8.3 Deployment Readiness
- ✅ All tests passing (unit, integration, functional)
- ✅ Code review approved
- ✅ Documentation complete
- ✅ Deployment guide tested
- ✅ Rollback plan documented

---

## 9. Glossary

- **Todo:** A single task item with title, description, target date
- **Tracker:** A record of status change with timestamp
- **Work Session:** Period between "Start Work" and "Done"
- **Status:** One of: New, Done, Failed, KIV, Started, Paused, Resumed
- **Target Date:** When a todo should be completed
- **Reschedule:** Change target_date (creates Status 8 record)
- **Time Taken:** Duration from Status 10 (Started) to Status 6 (Done)
- **Achievement:** Milestone reward for completing todos
- **Checklist Item:** Sub-task with checkbox within a todo

---

## 10. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | - | | |
| Development Lead | - | | |
| QA Lead | - | | |
| DevOps Lead | - | | |

---

**Document History:**
- **v1.0** (Jan 16, 2026) - Initial comprehensive SRS covering all implemented features and requirements

**Status:** ACTIVE - This SRS is the authoritative specification for TodoBox application development and testing.
