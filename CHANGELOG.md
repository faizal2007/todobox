# Changelog

All notable changes to TodoBox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
