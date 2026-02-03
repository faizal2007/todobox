# TodoBox Documentation Master Index

**Last Updated:** February 3, 2026  
**Status:** Current & Active  
**Active Documents:** 36 core documentation files  
**Archived Documents:** 80+ historical documents

---

## Quick Navigation

- [📋 System Requirements & Specifications](#system-requirements--specifications)
- [🏗️ Architecture & Design](#architecture--design)
- [🔧 Feature Implementation](#feature-implementation)
- [🧪 Testing & Quality](#testing--quality)
- [🚀 Deployment & Operations](#deployment--operations)
- [🔐 Security & Compliance](#security--compliance)
- [⏰ Time Tracking & Achievements](#time-tracking--achievements)
- [👤 User Management & Authentication](#user-management--authentication)
- [📅 Setup & Getting Started](#setup--getting-started)

---

## System Requirements & Specifications

### Primary Reference Documents

1. **[SYSTEM_REQUIREMENTS_SPECIFICATION.md](SYSTEM_REQUIREMENTS_SPECIFICATION.md)** ⭐ PRIMARY
   - Comprehensive SRS covering all functional and non-functional requirements
   - Technology stack and API endpoints
   - Acceptance criteria and sign-off
   - **Status:** CURRENT & COMPLETE
   - **When to Use:** Product planning, requirement validation, feature scope

2. **[REQUIREMENTS_ANALYSIS.md](REQUIREMENTS_ANALYSIS.md)**
   - Initial requirements analysis and user stories
   - Feature prioritization
   - **Status:** CURRENT
   - **When to Use:** Understanding original project goals

### Feature Status

3. **[FEATURE_COMPLETION_REPORT.md](FEATURE_COMPLETION_REPORT.md)**
   - Final report on all implemented features
   - Feature checklist with status
   - Known limitations and future enhancements
   - **Status:** CURRENT
   - **When to Use:** Checking what's completed

4. **[TODO_STATUS_VERIFICATION_REPORT.md](TODO_STATUS_VERIFICATION_REPORT.md)**
   - Verification that all todo statuses working correctly
   - Status workflow testing
   - **Status:** CURRENT
   - **When to Use:** Validating status transitions

---

## Architecture & Design

### System Architecture

5. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - Overall system architecture
   - Component interactions
   - Data flow diagrams
   - **Status:** CURRENT
   - **When to Use:** Understanding system structure

6. **[OVERVIEW.md](OVERVIEW.md)**
   - High-level project overview
   - Technology choices
   - System components
   - **Status:** CURRENT
   - **When to Use:** Project introduction

### API Documentation

7. **[API.md](API.md)**
   - RESTful API endpoint documentation
   - Request/response examples
   - Error codes
   - **Status:** CURRENT
   - **When to Use:** API integration and endpoint reference

### Data Models

8. **[MODELS.md](MODELS.md)**
   - Database schema and relationships
   - SQLAlchemy model definitions
   - Field descriptions
   - **Status:** CURRENT
   - **When to Use:** Database design and data structure reference

---

## Feature Implementation

### Work Session & Time Tracking

9. **[TIME_TAKEN_CALCULATION.md](TIME_TAKEN_CALCULATION.md)** ⭐ CRITICAL
   - How time tracking calculation works
   - Status 10 (Started) to Status 6 (Done) calculation
   - Progressive time display format (seconds → minutes → hours → days → years)
   - Code examples
   - **Status:** CURRENT
   - **When to Use:** Understanding time calculation, troubleshooting time display

10. **[TIME_TRACKING_WITH_RESCHEDULING_ANALYSIS.md](TIME_TRACKING_WITH_RESCHEDULING_ANALYSIS.md)**
    - Architectural analysis of time tracking with rescheduling
    - Why Status 10 is needed (accurate work time)
    - How reschedules don't affect time calculation
    - Migration path
    - **Status:** COMPLETE (IMPLEMENTED)
    - **When to Use:** Understanding time calculation design decisions

11. **[WORK_SESSION_MODAL_IMPLEMENTATION.md](WORK_SESSION_MODAL_IMPLEMENTATION.md)**
    - Work session modal UI implementation
    - Modal workflow (Start → Pause/End → Resume)
    - Button state machine
    - Auto-pause on modal close
    - **Status:** CURRENT & IMPLEMENTED
    - **When to Use:** Understanding work session modal functionality

12. **[WORK_SESSION_TRACKING_IMPLEMENTATION.md](WORK_SESSION_TRACKING_IMPLEMENTATION.md)**
    - Server-side tracking implementation
    - API endpoints for start/pause/resume
    - Database status tracking
    - **Status:** CURRENT & IMPLEMENTED
    - **When to Use:** Backend work session logic reference

### User Features

13. **[USER_CREATION.md](USER_CREATION.md)**
    - User account creation workflow
    - Registration validation
    - **Status:** CURRENT
    - **When to Use:** User registration implementation

14. **[USER_REGISTRATION_GUIDE.md](USER_REGISTRATION_GUIDE.md)**
    - User registration process guide
    - Email verification
    - OAuth integration
    - **Status:** CURRENT
    - **When to Use:** Registration feature reference

### Advanced Features

15. **[TIMEZONE_AUTO_DETECTION.md](TIMEZONE_AUTO_DETECTION.md)**
    - Automatic timezone detection from browser
    - Geolocation implementation
    - **Status:** CURRENT
    - **When to Use:** Timezone feature implementation

16. **[TIMEZONE_INTEGRATION.md](TIMEZONE_INTEGRATION.md)**
    - Timezone integration in application
    - How timezones affect scheduling and reminders
    - **Status:** CURRENT
    - **When to Use:** Timezone handling and testing

17. **[EMAIL_DELIVERABILITY.md](EMAIL_DELIVERABILITY.md)**
    - Email system implementation
    - SMTP configuration
    - Reminder email delivery
    - **Status:** CURRENT
    - **When to Use:** Email feature reference

18. **[AUTO_CLOSE_REMINDERS.md](AUTO_CLOSE_REMINDERS.md)**
    - Automatic reminder closing when todos completed
    - Reminder lifecycle
    - **Status:** CURRENT
    - **When to Use:** Reminder feature logic

19. **[KIV_STATUS.md](KIV_STATUS.md)**
    - Keep In View (KIV) status functionality
    - Pausing and postponing todos
    - **Status:** CURRENT
    - **When to Use:** KIV feature reference

### Authentication

20. **[OAUTH_SETUP.md](OAUTH_SETUP.md)**
    - OAuth 2.0 (Google) setup and configuration
    - Token management
    - **Status:** CURRENT
    - **When to Use:** OAuth implementation and configuration

### Code Quality & Standards

21. **[AXE_LINTER_BEST_PRACTICES.md](AXE_LINTER_BEST_PRACTICES.md)**
    - HTML/CSS accessibility linting rules
    - WCAG 2.1 compliance
    - Axe DevTools best practices
    - **Status:** CURRENT
    - **When to Use:** Accessibility validation and improvements

22. **[CODE_REVIEW.md](CODE_REVIEW.md)**
    - Code review guidelines and standards
    - Review checklist
    - **Status:** CURRENT
    - **When to Use:** Pull request reviews

---

## Testing & Quality

### Test Strategy

23. **[COMPREHENSIVE_TEST_STRATEGY.md](COMPREHENSIVE_TEST_STRATEGY.md)**
    - Complete testing strategy
    - Test types and coverage goals
    - Test execution plan
    - **Status:** CURRENT
    - **When to Use:** Test planning and execution

24. **[TESTING_STRATEGY_AND_CI_CD.md](TESTING_STRATEGY_AND_CI_CD.md)**
    - Testing strategy aligned with CI/CD
    - Automated test triggers
    - Pipeline configuration
    - **Status:** CURRENT
    - **When to Use:** CI/CD and automated testing reference

25. **[TESTING_SUMMARY.md](TESTING_SUMMARY.md)**
    - Summary of testing results
    - Test coverage metrics
    - Known test issues (if any)
    - **Status:** CURRENT
    - **When to Use:** Test result review

---

## Deployment & Operations

### Deployment

26. **[DEPLOYMENT.md](DEPLOYMENT.md)**
    - Deployment procedures
    - Environment setup
    - Release checklist
    - **Status:** CURRENT
    - **When to Use:** Production deployment

27. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
    - Pre-deployment checklist
    - Post-deployment verification
    - Rollback procedures
    - **Status:** CURRENT
    - **When to Use:** Deployment verification

28. **[DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md)**
    - Deployment readiness assessment
    - Production environment checklist
    - **Status:** CURRENT
    - **When to Use:** Pre-deployment review

### Setup & Installation

29. **[SETUP.md](SETUP.md)** ⭐ START HERE
    - Initial project setup
    - Dependencies installation
    - Database configuration
    - Running the application
    - **Status:** CURRENT
    - **When to Use:** Getting the app running

30. **[QUICKSTART.md](QUICKSTART.md)**
    - Quick start guide for new developers
    - Essential first steps
    - Common commands
    - **Status:** CURRENT
    - **When to Use:** Rapid onboarding

31. **[README.md](README.md)**
    - Project README
    - High-level overview
    - Key features
    - **Status:** CURRENT
    - **When to Use:** Project introduction

32. **[README_MIGRATIONS.md](README_MIGRATIONS.md)**
    - Database migrations guide
    - Alembic usage
    - Migration management
    - **Status:** CURRENT
    - **When to Use:** Database schema changes

---

## Security & Compliance

### Security

33. **[SECURITY_AUDIT.md](SECURITY_AUDIT.md)**
    - Comprehensive security audit
    - Vulnerability assessment
    - Security recommendations
    - **Status:** CURRENT
    - **When to Use:** Security review and compliance

34. **[SECURITY_FIX_CREDENTIALS.md](SECURITY_FIX_CREDENTIALS.md)**
    - Credentials security best practices
    - Secret management
    - Environment configuration
    - **Status:** CURRENT
    - **When to Use:** Credential handling reference

---

## Archived Documents

### Legacy Documentation (33 items)

These documents have been archived as they represent:
- Specific bug fixes (already implemented)
- Old test reports (superseded by current tests)
- Implementation details (code is source of truth)
- Analysis documents (conclusions implemented)
- Temporary notes (no longer needed)

**Archived Documents Location:** [archive/](archive/)

**Archived Items Include:**
- ACHIEVEMENT_MODAL_BUG_FIX.md
- BULLET_POINT_ISSUE_FIX.md
- CHECKBOX_HTML_RENDERING_IMPLEMENTATION.md
- DECISION_KEEP_AS_IS.md
- DONUT_CHART_FIX.md
- FEATURE_TEST_RESULTS_DECEMBER_16_2025.md
- FULL_CYCLE_TEST_SUMMARY.txt
- JAVASCRIPT_OPTIMIZATION.md
- JQUERY_MIGRATION_GUIDE.md
- LOCAL_VS_PRODUCTION_ANALYSIS.md
- MIGRATION_FIX_GUIDE.md
- QA_IMPROVEMENTS_SUMMARY.md
- REASSIGN_PENDING_LOGIC_ANALYSIS.md
- REGISTRATION_IMPLEMENTATION_SUMMARY.md
- REGISTRATION_QUICK_REFERENCE.md
- REORGANIZATION_NOTES.md
- SECURITY_PATCHES.md
- SESSION_SUMMARY.md
- STATUS_LOGIC_USER_SUMMARY.md
- STRIKETHROUGH_IMPLEMENTATION.md
- TEST_COVERAGE_GAP_KIV_FIX.md
- TEST_FAILURE_ANALYSIS.md
- TEST_FAILURE_ROOT_CAUSE_ANALYSIS.md
- TEST_INVENTORY.md
- TEST_SUITE_COMPREHENSIVE.md
- TEST_SUITE_REVISION_SUMMARY.md
- TEST_UPDATE_SUMMARY.md
- TESTING_COMPLETE.md
- DOCUMENTATION_UPDATE_DECEMBER_9_2025.md
- WHY_TESTS_DIDNT_CATCH_BUG.md
- FLOATING_PROGRESS_WIDGET.md
- ON_THE_FLY_MODE_SWITCHING.md

**When to Access Archive:** Only for historical reference or understanding past decisions.

---

## Documentation Guidelines

### How to Use This Index

1. **New to Project?** Start with: [SETUP.md](SETUP.md) → [QUICKSTART.md](QUICKSTART.md) → [SYSTEM_REQUIREMENTS_SPECIFICATION.md](SYSTEM_REQUIREMENTS_SPECIFICATION.md)

2. **Implementing a Feature?** Find in [Feature Implementation](#feature-implementation) section

3. **Deploying to Production?** Follow [Deployment & Operations](#deployment--operations) section

4. **Code Review?** Check [CODE_REVIEW.md](CODE_REVIEW.md) and [AXE_LINTER_BEST_PRACTICES.md](AXE_LINTER_BEST_PRACTICES.md)

5. **Understanding Time Tracking?** Read [TIME_TAKEN_CALCULATION.md](TIME_TAKEN_CALCULATION.md) + [WORK_SESSION_MODAL_IMPLEMENTATION.md](WORK_SESSION_MODAL_IMPLEMENTATION.md)

### Document Status Legend

- ⭐ **PRIMARY** - Essential reference document
- ✅ **CURRENT** - Up-to-date and accurate
- 📋 **IMPLEMENTED** - Feature is code-complete and tested
- ⚠️ **PARTIAL** - Some sections may be outdated
- 🔄 **IN PROGRESS** - Document actively being updated

---

## Key Implementation Highlights

### ✅ Completed Features

1. **Work Session Modal** (v1.0)
   - User clicks Start Work button
   - Modal displays timer (HH:MM:SS)
   - Start → Pause/End workflow
   - Auto-pause on modal close
   - State preserved for resume
   - Reference: [WORK_SESSION_MODAL_IMPLEMENTATION.md](WORK_SESSION_MODAL_IMPLEMENTATION.md)

2. **Accurate Time Tracking** (v1.0)
   - Time = Status 10 (Started) → Status 6 (Done)
   - Excludes planning and reschedule time
   - Progressive display format
   - Reference: [TIME_TAKEN_CALCULATION.md](TIME_TAKEN_CALCULATION.md)

3. **User Authentication**
   - Email/password registration and login
   - Google OAuth 2.0 integration
   - Session management
   - Reference: [OAUTH_SETUP.md](OAUTH_SETUP.md), [USER_REGISTRATION_GUIDE.md](USER_REGISTRATION_GUIDE.md)

4. **Todo Management**
   - Create, edit, reschedule, complete todos
   - Multiple status transitions
   - Checklist items with checkboxes
   - References: [SYSTEM_REQUIREMENTS_SPECIFICATION.md](SYSTEM_REQUIREMENTS_SPECIFICATION.md), [MODELS.md](MODELS.md)

5. **Email Reminders**
   - Scheduled reminder emails
   - Auto-close on completion
   - Reference: [EMAIL_DELIVERABILITY.md](EMAIL_DELIVERABILITY.md), [AUTO_CLOSE_REMINDERS.md](AUTO_CLOSE_REMINDERS.md)

6. **Timezone Support**
   - Auto-detection from browser
   - Manual timezone selection
   - All calculations in user's timezone
   - References: [TIMEZONE_AUTO_DETECTION.md](TIMEZONE_AUTO_DETECTION.md), [TIMEZONE_INTEGRATION.md](TIMEZONE_INTEGRATION.md)

---

## Contact & Support

- **Project Repository:** `/storage/linux/Projects/mysandbox`
- **Documentation Location:** `/storage/linux/Projects/mysandbox/docs`
- **Archive Location:** `/storage/linux/Projects/mysandbox/docs/archive`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 16, 2026 | Initial comprehensive index, archived 33 obsolete documents, created SRS |

---

**Last Updated:** January 16, 2026  
**Status:** ACTIVE - This is the authoritative documentation index for TodoBox project
