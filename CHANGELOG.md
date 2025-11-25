# Changelog

## [Latest] - 2025-11-26

### Added

- Wisdom Quotes Integration with ZenQuotes API and local fallback
- Gravatar user avatars with identicon fallback
- Current date display in user dropdown using moment.js
- `/api/quote` Flask endpoint for server-side quote fetching

### Changed

- Simplified quote API to use only ZenQuotes (removed Quotable)
- Navigation items hidden from anonymous users
- Font optimization - removed unused BungeeShade-Regular.ttf preload
- Added `referrerpolicy="no-referrer"` to Gravatar images

### Fixed

- CORS policy errors by moving API calls to server-side
- JavaScript null reference errors for current-date element
- Font loading performance warnings
