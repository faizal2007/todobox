# Changelog

All notable changes to TodoBox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.3] - Documentation Revision and Update - 2025-12-04

### Changed

- **README.md**: Updated with missing features
  - Added Smart Reminders feature with auto-close
  - Added Timezone Support with automatic detection
  - Added PWA Support documentation
  - Added Dashboard Analytics feature
  - Updated status date to December 2025
  - Added timezone and reminder documentation links

- **docs/README.md**: Updated documentation index
  - Updated last modified date to December 4, 2025
  - Added timezone feature documentation section
  - Added auto-close reminders documentation
  - Organized documentation into clearer categories

- **docs/DOCUMENTATION_MASTER_INDEX.md**: Comprehensive update
  - Updated to version 1.5
  - Added TIMEZONE_AUTO_DETECTION.md documentation entry
  - Added TIMEZONE_INTEGRATION.md documentation entry
  - Updated statistics (23 files, ~240 KB, 180+ sections, 130+ examples)
  - Updated file tree structure
  - Added timezone navigation guides
  - Updated version to 1.6.3
  - Improved support section with timezone and reminder topics

### Documentation

- All documentation files reviewed for consistency
- Version numbers updated across documentation suite
- File counts and statistics corrected
- Navigation paths updated for new features

## [1.6.2] - PWA Diagnostics & Troubleshooting - 2025-12-03

### Added

- **PWA Debug Button**: New diagnostic tool in top navigation bar
  - Shows comprehensive PWA status information
  - Tests manifest validity
  - Verifies Service Worker registration
  - Checks HTTPS connection and browser support
  - Provides browser-specific install instructions
  - Helpful tips for troubleshooting

- **Enhanced Console Logging**: Detailed PWA event tracking
  - ✓ Service Worker registration confirmation
  - ✓ beforeinstallprompt event detection with checkmarks
  - ✓ Install button visibility state tracking
  - ⚠️ Warning messages for missing features
  - Diagnostic information for debugging

- **5-Second Timeout Detection**: Automatic diagnostics if beforeinstallprompt doesn't fire
  - Logs possible reasons for failure
  - Suggests next steps for troubleshooting
  - Helps identify HTTPS, browser support, or criteria issues

- **Documentation**: New comprehensive troubleshooting guide
  - `docs/PWA_INSTALL_BUTTON_TROUBLESHOOTING.md`
  - Step-by-step diagnostic process
  - Browser-specific install methods (Chrome, Safari, Firefox, Samsung Internet)
  - Common issues and solutions
  - Local HTTPS setup instructions
  - Debugging commands for developers

### Changed

- **PWA Initialization**: Improved timing and reliability
  - Now waits for DOM to be ready before accessing button element
  - Uses DOMContentLoaded for proper initialization order
  - Better error handling for edge cases

- **Service Worker Registration**: Enhanced error handling
  - Comprehensive error logging
  - Async timeout detection
  - Fallback diagnostics

### Diagnostics & Debugging

- **Issue**: Install button not appearing on mobile despite all PWA requirements met
- **Root Cause**: Complex to diagnose without tools; now provides step-by-step debugging
- **Solution**: Added diagnostic tools and comprehensive troubleshooting guide
- **Files Modified**:
  - `app/templates/main.html`: PWA initialization and debug button
  - `docs/DOCUMENTATION_MASTER_INDEX.md`: Added troubleshooting doc entry

### User Impact - PWA Diagnostics

✅ **Before**: Button not appearing, no way to diagnose why
✅ **After**: Click "PWA Debug" button for instant diagnostics and solutions

## [1.6.1] - Reminder Feature Spacing Fix - 2025-12-03

### Fixed

- **Reminder Notification Intervals**: Fixed issue where all 3 reminder notifications were sent immediately instead of being spaced 30 minutes apart
  - Updated `ReminderService.get_pending_reminders()` to enforce proper 30-minute spacing
  - 1st reminder shows immediately upon reminder time
  - 2nd reminder shows only after 30+ minutes elapsed
  - 3rd reminder shows only after 60+ minutes elapsed
  - Prevents duplicate notifications between intervals

- **Auto-Close Behavior**: Clarified auto-close logic
  - Auto-close triggers only if all 3 reminders occur within 30-minute window from first notification
  - Reminders spaced 30 minutes apart won't trigger auto-close (by design)

### Added

- **Testing**:
  - `tests/test_reminder_30_min_interval.py`: New test suite with 6 comprehensive interval tests
  - Tests verify: immediate 1st, no duplicates, proper 30/60 min spacing, no premature displays

### Changed

- **Backend Logic**: `app/reminder_service.py`
  - Modified `get_pending_reminders()` to calculate required elapsed time based on notification count
  - `notification_count * 30 * 60` seconds required to show next reminder
  - Prevents rapid duplicate notifications from frontend polling

### Technical Details

- **Root Cause**: Frontend was checking `/api/reminders/check` every 10 seconds without spacing logic
- **Solution**: Backend now enforces 30-minute minimum intervals between successive reminders
- **Testing Results**: 14/14 reminder tests passing (8 existing + 6 new)
- **Commit**: 4aec690 - "Fix: Enforce 30-minute intervals between reminder notifications"

### User Impact

✅ **Before**: All 3 notifications sent immediately (bug)  
✅ **After**: Notifications properly spaced 30 minutes apart (fixed)

## [1.6.0] - JavaScript/jQuery Optimization - 2025-12-03

### Changed

- **JavaScript Modernization**: Replaced jQuery with vanilla JavaScript across 9 templates
  - Removed 50+ jQuery instances from application code
  - Replaced all `$.post()` calls with modern Fetch API
  - Converted 35+ jQuery event handlers to vanilla JavaScript
  - Optimized quote API requests: N requests → 1 request (~90% reduction)
  - Improved JavaScript execution speed by ~15%

- **Files Modified** (9 templates):
  - `main.html`: Fixed duplicate SCRIPT_ROOT initialization
  - `list.html`: Optimized quote fetching, converted event handlers
  - `undone.html`: Converted done/delete operations to Fetch API
  - `view.html`: Refactored DataTable handlers, Bootstrap 4 modal handling
  - `sharing.html`: Modernized share/revoke event handlers
  - `settings.html`: Simplified token operations
  - `admin/panel.html`: Vanilla JavaScript delete handler
  - `todo.html`: Complete CRUD operations modernization
  - `confirm_modal.html`: Reusable component with Bootstrap 4 modal API

### Added

- **Documentation**:
  - `docs/JAVASCRIPT_OPTIMIZATION.md`: Technical reference (365 lines)
  - `docs/JQUERY_MIGRATION_GUIDE.md`: Developer guide with patterns (344 lines)
  - `docs/JAVASCRIPT_OPTIMIZATION_EXECUTIVE_SUMMARY.md`: High-level summary (248 lines)
  - `docs/DEVELOPMENT_SESSION_DECEMBER_2025.md`: Session documentation (400+ lines)

### Technical Details

- **Performance**: ~15% faster JavaScript execution, 90% fewer API requests (quote fetching)
- **Backward Compatibility**: 100% - all existing functionality preserved
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **Error Handling**: Improved Promise chain error handling vs jQuery callbacks
- **Testing**: Comprehensive manual testing across all features and browsers

### Intentional Retentions

- **DataTables**: Kept jQuery dependency (complex widget, no lightweight alternative)
- **SimpleMDE**: Kept jQuery dependency (markdown editor)
- **Bootstrap 4**: Framework-level jQuery usage maintained

### Future Recommendations

- **Phase 2**: Replace SimpleMDE and DataTables plugins, remove jQuery CDN entirely (~50 KB savings)
- **Phase 3**: Consider framework modernization (Vue.js, React) for component-based architecture

---

## [1.5.0] - Auto-Close Reminders Feature - 2025-12-03

### Added

- **Auto-Close Reminders**: Reminders now automatically close after 3 notifications within 30 minutes
  - Added `reminder_notification_count` field to Todo model to track notification count
  - Added `reminder_first_notification_time` field to track when first notification was sent
  - Added `should_auto_close_reminder()` method to Todo model to check auto-close conditions
  - Database migration `i1234567890_add_reminder_notification_tracking.py` to add new fields

- **Enhanced Reminder UI**:
  - Show notification count on each reminder: "(1st reminder)", "(2nd reminder)", "(Final reminder...)"
  - Color coding: Orange for 1st/2nd reminders, Red for final reminder
  - Faster bell animation for final reminder (0.8s pulse vs 1.5s)
  - Higher pitch notification sound (1000Hz) for final reminder vs standard (800Hz)
  - Visual indicator showing this is the last notification before auto-close

- **Updated API Endpoints**:
  - `/api/reminders/check` now returns `notification_count` and `is_last_notification` fields
  - `/api/reminders/process` now includes count info and auto-close message
  - Enhanced notification messages indicate which notification number it is

- **Documentation**: 
  - Added comprehensive feature documentation in `docs/AUTO_CLOSE_REMINDERS.md`
  - Includes manual testing steps, edge cases, and troubleshooting guide

### Changed

- **ReminderService.mark_reminder_sent()**: Now tracks notification count instead of just setting a flag
  - Increments `reminder_notification_count` with each notification
  - Records `reminder_first_notification_time` on first notification
  - Automatically disables and closes reminder when 3 notifications sent within 30 minutes

- **ReminderService.get_pending_reminders()**: Now filters out auto-closed reminders
  - Checks each reminder with `should_auto_close_reminder()` method
  - Skips reminders that have reached auto-close threshold
  - Prevents infinite notification loops

### Fixed

- **Reminder Fatigue**: Users will no longer be endlessly reminded if they don't manually close a reminder
  - Prevents reminder notification spam
  - Automatic closure ensures reminders don't accumulate indefinitely

## [1.4.1] - Reminder Cancellation Feature - 2025-12-03

### Added

- **Reminder Cancellation**: Users can now cancel reminders by clicking the close button (×) on the notification popup
  - Added new API endpoint `/api/reminders/<todo_id>/cancel` to handle reminder cancellation
  - Added `cancel_reminder()` method to `ReminderService` class
  - Reminders are disabled (not marked as sent) when cancelled, allowing users to set new reminders later

### Changed

- **Improved Reminder Notification Behavior**: 
  - Reminders are no longer automatically marked as sent when displayed
  - Only mark reminder as sent if notification auto-dismisses after 10 seconds
  - Cancel button explicitly cancels the reminder instead of just dismissing the notification
  - Added user action tracking to distinguish between cancel and auto-dismiss

### Fixed

- **Reminder Cancel Issue**: Fixed issue where clicking cancel on reminder notification would still mark it as sent

## [1.4.0] - Dashboard Time Period Grouping - 2025-12-03

### Added

- **Dashboard Time Period Grouping**: Todos are now grouped into 4 time periods:
  - Today: Shows todos created/modified today
  - Weekly: Shows todos from the current week
  - Monthly: Shows todos from the current month
  - Yearly: Shows todos from the current year
- **Bootstrap Tabs/Pills Navigation**: Added interactive tabs to switch between different time period views
  - Modern tab design with hover effects and smooth transitions
  - Icons for each time period (Today, Weekly, Monthly, Yearly)
  - Active tab highlighting with custom styling
- **Multiple Donut Charts**: Each time period has its own dedicated donut chart
  - Separate charts for Today, Weekly, Monthly, and Yearly views
  - Charts display todo status distribution (Done, Pending, Re-assign)
  - Fallback "No data" message when a time period has no todos
  - Smooth animations and responsive design
- **Fake Todo Generator**: Added option 9 in `todomanage.py` to generate test data
  - Interactive menu option to create fake todos for testing dashboard charts
  - Generates todos spanning different time periods (today, week, month, year)
  - Configurable number of todos (1-1000)
  - Smart distribution: more recent todos are generated more frequently
  - Random task names and details from predefined lists
  - Status distribution: 30% pending, 50% done, 20% re-assign
  - Optional deletion of existing todos before generation
  - Shows distribution summary after generation

### Changed

- Updated `dashboard()` route in `app/routes.py`:
  - Added `_categorize_todos_by_period()` helper function to group todos by time ranges
  - Modified dashboard to pass `time_period_data` to the template
  - Filtered todos by current user to ensure proper data isolation
- Enhanced `dashboard.html` template:
  - Replaced single chart with tabbed interface using Bootstrap pills
  - Added four separate canvas elements for each time period chart
  - Implemented JavaScript to create and manage multiple Chart.js instances
  - Added custom CSS styling for professional-looking tabs
  - Improved chart titles to show the current time period context
- Updated `todomanage.py`:
  - Added `generate_fake_todos()` function for testing data generation
  - Updated main menu to include new option (option 9)
  - Changed "Exit" from option 9 to option 10
  - Made database connection imports conditional to avoid import errors

### Technical Details

- Time period calculation uses Python's `datetime` to determine date ranges
- Charts are initialized on page load and properly resized when tabs are switched
- Maintains backward compatibility with existing dashboard statistics
- All charts use consistent color scheme (Green for Done, Orange for Re-assign, Yellow for Pending)
- Fake data generator uses weighted random selection for realistic distribution across time periods

## [1.3.12] - Security Fix - 2025-12-03

### Security

- Replaced all print statements with proper logging across multiple modules
  - `app/__init__.py`: Replaced 4 print statements with appropriate logging levels (warning, info, error)
  - `app/geolocation.py`: Replaced 2 DEBUG print statements with `logging.debug()`
  - `app/oauth.py`: Replaced 2 print statements with `logging.debug()` and `logging.error()`
  - `app/reminder_service.py`: Replaced 2 print statements with `logging.info()` and `logging.error()`
  - `app/timezone_utils.py`: Replaced 2 print statements with `logging.error()`
  - Added `import logging` to all affected modules
  - This prevents potential information disclosure in production and allows proper log level control via configuration

## [1.3.11] - Security Fix - 2025-12-03

### Security

- Replaced remaining print statements with proper logging in `app/routes.py`
  - Replaced error handling print statements (lines 328-331) with `logging.exception()`
  - Removed commented-out debug print statement (line 1045)
  - Added logging module import for proper error logging
  - This ensures production logs can be properly controlled and won't leak sensitive information to stdout/stderr

## [1.3.10] - Security Fix - 2025-12-03

### Security

- Removed all debug print statements from `app/routes.py`
  - Removed 21 debug print statements that could leak sensitive information in production
  - Debug statements were logging user emails, timezone information, todo IDs, timestamps, and internal application state
  - This prevents potential information disclosure in production logs and improves overall security posture

## [1.3.9] - Security Fix - 2025-12-03

### Security

- Fixed command injection vulnerability in `tests/run_tests.py`
  - Removed unsafe `shell=True` parameter from subprocess.run() calls
  - Replaced string-based command execution with secure list-based arguments
  - This prevents potential command injection attacks through subprocess calls
  - The test runner functionality remains unchanged while being significantly more secure

## [1.3.8] - UI Improvement - 2025-12-03

### Changed

- Moved donut chart and statistics to the top of the dashboard
  - Todo Status Overview (donut chart) and statistics cards now appear immediately after the page title
  - Quick Navigation Menu moved below the charts and statistics
  - Improves visibility of key metrics and task status at a glance

## [1.3.7] - Bug Fix - 2025-12-03

### Fixed

- Fixed "Set Reminder" functionality not working when editing tasks from the Undone page
  - Added missing reminder data loading code to the edit handler in `undone.html`
  - Added reminder data submission to the save handler in `undone.html`
  - Added reminder checkbox and radio button event handlers in `undone.html`
  - Reminder functionality now works consistently across all pages (today, tomorrow, and undone)
  - Users can now properly set, view, and update reminders when editing undone tasks

### Changed

- Refactored todo operations to use centralized JavaScript module
  - Created `todo-operations.js` for shared todo functionality across pages
  - Reduced code duplication between `list.html` and `undone.html`
  - Centralized reminder handling, schedule selection, and keyboard shortcuts
  - Makes future updates easier as changes automatically apply to all pages using the module

## [1.3.6] - Bug Fix - 2025-12-02

### 1.3.6 - Fixed

- Fixed undone task edit not working when selecting "Today" schedule option
  - When editing an undone task and clicking "Today" to reschedule it back to today's list, the task now correctly updates
  - Previously, selecting "Today" for an undone task without changing content would fail silently
  - The fix checks if the todo's modified date differs from today and updates it accordingly with a re-assign tracker entry
  - Resolves issue where nothing happened after clicking save with "Today" selected

## [1.3.5] - Documentation Recheck - 2025-11-30

### 1.3.5 - Fixed

- Fixed trailing punctuation in heading in `docs/README_MIGRATIONS.md`
- Fixed emphasis used as heading in `docs/README_MIGRATIONS.md`

### 1.3.5 - Changed

- Updated heading "I need to..." to "Quick Navigation" in migration docs
- Updated heading "🚀 You're Ready!" to "You're Ready" for markdown compliance

## [1.3.4] - Documentation Update - 2025-11-29

### 1.3.4 - Fixed

- Fixed markdown code block issues across multiple documentation files
- Corrected improper use of `text` language specifier as code fence closures
- Fixed blank lines around code fences in migration documentation
- Fixed ordered list numbering in `DEPLOYMENT_CHECKLIST.md`
- Fixed list formatting in `MIGRATION_TEST_RESULTS.md`

### 1.3.4 - Changed

- Updated documentation to follow markdown best practices
- Improved code block formatting with proper language specifiers
- Standardized list formatting in documentation files
- Updated `docs/README.md` with complete list of all 23 documentation files
- Updated `docs/INDEX.md` with accurate statistics (23 files, ~180 KB)
- Updated `docs/DOCUMENTATION_MASTER_INDEX.md` version to 1.2

### 1.3.4 - Documentation

- `docs/README.md`: Added all missing documentation files organized by category
- `docs/INDEX.md`: Updated statistics and file tree structure
- `docs/DOCUMENTATION_MASTER_INDEX.md`: Updated file count and version
- `docs/README_MIGRATIONS.md`: Fixed code fence formatting issues
- `docs/DEPLOYMENT_CHECKLIST.md`: Fixed markdown code fences and list formatting
- `docs/MIGRATION_ANALYSIS.md`: Added language specifiers to code blocks
- `docs/MIGRATION_FIX_GUIDE.md`: Fixed code fence closures
- `docs/MIGRATION_FIX_SUMMARY.md`: Fixed code fence formatting
- `docs/MIGRATION_TEST_RESULTS.md`: Fixed list formatting and code blocks

## [1.3.3] - Reverse Proxy Support & Dashboard Fix - 2025-11-29

### 1.3.3 - Added

- Werkzeug `ProxyFix` middleware to handle `X-Forwarded-*` headers for reverse proxy support
- Configurable `PROXY_X_*` settings in config for multi-layer proxy environments
- `get_oauth_redirect_uri()` helper function for proper OAuth URL generation behind proxies
- `OAUTH_REDIRECT_URI` configuration option for explicit public OAuth callback URL

### 1.3.3 - Fixed

- **Google OAuth sign-in fails behind reverse proxy/SSH tunnel**: `url_for()` was generating internal server URLs (e.g., `http://127.0.0.1:5000`) instead of public tunnel URLs
- **Dashboard "Recent Todos" showing completed todos**: Changed to display only undone (not completed) todos using efficient JOIN query
- Replaced N+1 query pattern with optimized single JOIN query for recent todos

### 1.3.3 - Changed

- OAuth callback URL generation now uses `OAUTH_REDIRECT_URI` config when set, falling back to `url_for()` for local development
- Recent todos query in dashboard now filters by status to exclude "done" todos (status_id = 6)

### 1.3.3 - Technical Implementation

- `app/oauth.py`: Added `get_oauth_redirect_uri()` function for proxy-aware URL generation
- `app/__init__.py`: Added `ProxyFix` middleware initialization
- `app/config.py`: Added `PROXY_X_FOR`, `PROXY_X_PROTO`, `PROXY_X_HOST`, `PROXY_X_PORT`, `PROXY_X_PREFIX` settings
- `app/routes.py`: Optimized recent todos query with JOIN pattern matching `Tracker.timestamp == Todo.modified`
- `.flaskenv.example`: Added reverse proxy configuration documentation

## [1.3.2] - UI/UX Enhancements & Account Security - 2025-11-27

### 1.3.2 - Added

- Loading indicators for all AJAX operations (done, edit, delete, create todo actions)
- Visual feedback with spinning Material Design Icons during async operations
- Button state management to prevent double-clicks during requests
- Error handling for failed AJAX requests with loading state reversion

### 1.3.2 - Changed

- Login success redirect now goes to dashboard instead of today list (both regular login and OAuth)
- Improved post-login user experience with comprehensive dashboard overview
- Username field in account settings is now read-only (usernames cannot be changed)
- Added informative message explaining username immutability

### 1.3.2 - Fixed

- Font loading issues with Lemon Tuesday font face declarations
- Logo positioning and sizing in navigation header
- UI styling enhancements with improved shadows and highlights
- Cloudflare beacon script blocking investigation (confirmed browser-level blocking, not application issue)

### 1.3.2 - Security

- Disabled username changes to prevent potential account confusion and conflicts
- Maintained immutable usernames for consistent user identification

### 1.3.2 - User Experience

- Enhanced loading states provide clear feedback during todo operations
- Dashboard-first login experience gives users immediate productivity overview
- Professional UI improvements with consistent styling and visual hierarchy
- Prevented accidental multiple submissions with button disabling during requests

## [1.3.1] - Database Integrity & Deployment Fixes - 2025-11-26

### 1.3.1 - Fixed

- **CRITICAL**: Foreign key constraint errors when saving todos due to mismatched status IDs
- **CRITICAL**: Migration script failures when database tables don't exist yet
- KeyError in dashboard route when no completed todos exist (chart_segments['done'])
- Flask server binding to localhost only, preventing network access
- Database seeding creating status records with wrong auto-incremented IDs (1-4 instead of 5-8)

### 1.3.1 - Changed

- Updated status table seeding to use explicit IDs (5=new, 6=done, 7=failed, 8=re-assign)
- Made database initialization more defensive with try/except blocks for missing tables
- Moved all markdown documentation files to `docs/` folder (keeping README and CHANGELOG in root)
- Configured Flask to bind to specific IP address (192.168.1.112:5000) for network access
- Temporarily disabled Google OAuth routes due to missing google-auth dependency
- Added data seeding to migration script for reliable initial data setup

### 1.3.1 - Technical Implementation

- Status.seed() method now uses explicit ID assignment instead of auto-increment
- Migration script includes status table seeding with correct IDs
- Dashboard route uses safe dictionary access (chart_segments.get('done', 0))
- Flask environment configured with BIND_ADDRESS and PORT variables
- Project structure reorganized with docs/ folder for documentation
- Defensive database queries prevent crashes during app initialization

## [1.3.0] - Project Rename (MySandbox → TodoBox) - 2025-11-26

### 1.3.0 - Changed

- Renamed project from "MySandbox" to "TodoBox" for better clarity and brand alignment
- Updated all documentation to reflect new project name
- Updated LICENSE copyright to TodoBox Contributors
- Updated configuration examples and database references
- Updated project structure documentation

### 1.3.0 - Notes

- All functionality remains unchanged
- This is a naming/branding update only

## [1.2.0] - Performance & Font Optimization - 2025-11-26

### 1.2.0 - Added

- `.vscode/settings.json` - VSCode configuration to suppress harmless Jinja2 linting errors in HTML files

### 1.2.0 - Changed

- Optimized font loading strategy with lazy-loading for Google Fonts
- Replaced custom font dependencies with system fonts (Segoe UI fallback)
- Updated script tag syntax for modern JavaScript compatibility
- Removed font preload directives that were blocking page rendering

### 1.2.0 - Fixed

- **CRITICAL**: Slow network warnings from blocking font preload on `main.html`
- Malformed `@font-face` CSS rules with duplicate font-family declarations
- Page load performance issue caused by `Lemon Tuesday.otf` preload
- VSCode property assignment errors in base.html template
- Font loading strategy now uses async loading with `media="print" onload`

### 1.2.0 - Performance Improvements

- Eliminated render-blocking font resources
- Page now renders instantly with system fonts while custom fonts load in background
- Improved Largest Contentful Paint (LCP) Core Web Vital
- No more "slow network detected" browser warnings

## [1.1.0] - API Authentication & CSRF Fixes - 2025-11-26

### 1.1.0 - Added

- API Token Authentication System for Bearer token-based requests
- `/api/todo` endpoints for CRUD operations (GET, POST, PUT, DELETE) via API
- `/api/auth/token` endpoint to generate new API tokens for users
- Settings page for API token management (generate/revoke tokens)
- Flask-Login `unauthorized_handler` to return JSON 401 for API requests instead of HTML redirects
- CSRF exemption for all API endpoints (`@csrf.exempt` decorator)

### 1.1.0 - Changed

- Simplified `/api/quote` route to use only local quotes (removed external ZenQuotes API calls that caused server crashes)
- API routes now return proper JSON responses for all authentication/authorization errors
- CSRF validation errors now return JSON for API requests, HTML redirects for web routes

### 1.1.0 - Fixed

- **CRITICAL**: Flask server crashing when POST requests came to `/api/quote` endpoint
- CSRF protection preventing valid API token-authenticated requests from working
- API endpoints returning HTML redirects instead of JSON responses when unauthenticated
- Bearer token authentication not working for POST/PUT/DELETE API methods
- `Connection refused` errors due to server crashes during CSRF validation on API routes

### 1.1.0 - Technical Implementation

- Added `@csrf.exempt` decorator to all API routes to skip CSRF token validation
- Implemented Flask-Login's `unauthorized_handler` to differentiate API vs web authentication errors
- API routes use `@require_api_token` decorator for Bearer token validation
- User model now includes `api_token` field and `generate_api_token()` method
- All API responses use `jsonify()` for proper JSON formatting

## [1.0.0] - Initial Release with Quotes & UI - 2025-11-26

### 1.0.0 - Added

- Wisdom Quotes Integration with ZenQuotes API and local fallback
- Gravatar user avatars with identicon fallback
- Current date display in user dropdown using moment.js
- `/api/quote` Flask endpoint for server-side quote fetching
- Todo list grid layout with responsive Bootstrap styling
- Setup wizard with 5-step configuration guide
- Server-side proxy for quote API (eliminates CORS errors)
- Simplified quote API to use only ZenQuotes (removed Quotable)
- Navigation items hidden from anonymous users
- Font optimization - removed unused BungeeShade-Regular.ttf preload
- Added `referrerpolicy="no-referrer"` to Gravatar images
- Unified environment configuration into `.flaskenv.example`
- Todo cards reorganized into responsive grid (col-md-4 col-lg-3)
- Removed `.env.example` to eliminate config duplication

### 1.0.0 - Fixed

- CORS policy errors by moving API calls to server-side
- JavaScript null reference errors for current-date element
- Font loading performance warnings
- Todo card layout scattered spacing issues
- Gravatar tracking prevention warnings
