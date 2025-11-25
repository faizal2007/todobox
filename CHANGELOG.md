# Changelog

## [Latest] - 2025-11-26

### Added

- Wisdom Quotes Integration with ZenQuotes API and local fallback
- Gravatar user avatars with identicon fallback
- Current date display in user dropdown using moment.js
- `/api/quote` Flask endpoint for server-side quote fetching
- Todo list grid layout with responsive Bootstrap styling
- Setup wizard with 5-step configuration guide
- Server-side proxy for quote API (eliminates CORS errors)

### Changed

- Simplified quote API to use only ZenQuotes (removed Quotable)
- Navigation items hidden from anonymous users
- Font optimization - removed unused BungeeShade-Regular.ttf preload
- Added `referrerpolicy="no-referrer"` to Gravatar images
- Unified environment configuration into `.flaskenv.example`
- Todo cards reorganized into responsive grid (col-md-4 col-lg-3)
- Removed `.env.example` to eliminate config duplication

### Fixed

- CORS policy errors by moving API calls to server-side
- JavaScript null reference errors for current-date element
- Font loading performance warnings
- Todo card layout scattered spacing issues
- Gravatar tracking prevention warnings
