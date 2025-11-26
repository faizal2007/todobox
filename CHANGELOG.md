# Changelog

All notable changes to TodoBox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
