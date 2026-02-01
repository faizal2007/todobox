# Test File Organization

**Date:** February 1, 2026  
**Status:** Complete  
**Purpose:** Document the location and purpose of all test and verification files

---

## Overview

All test and verification files are now centralized in the `tests/` folder for better organization and maintainability. This document provides a comprehensive guide to test file locations and their purposes.

---

## Test File Locations

### Test Scripts (Python)

All Python test files are located in `tests/` directory:

```bash
tests/
├── test_accurate_comprehensive.py       # Core functionality tests (9 tests)
├── test_achievement_modal_endpoint.py   # Achievement modal endpoint tests
├── test_achievements.py                 # Achievement system tests
├── test_achievements_time_calculation.py # Achievement time calculation tests
├── test_all_routes.py                   # All routes comprehensive tests
├── test_backend_routes.py               # Backend route tests
├── test_backup.py                       # Backup functionality tests
├── test_checkbox_html_conversion.py     # Checkbox HTML rendering tests (moved from root)
├── test_comprehensive.py                # Comprehensive test suite
├── test_cooldown_expiry.py              # Cooldown expiry tests
├── test_deleted_account_block.py        # Deleted account blocking tests
├── test_email_direct.py                 # Direct email tests
├── test_email_headers.py                # Email header tests
├── test_email_send.py                   # Email sending tests
├── test_features_comprehensive.py       # Feature comprehensive tests
├── test_frontend.py                     # Frontend tests
├── test_frontend_assets.py              # Frontend asset tests (20+ tests)
├── test_functional.py                   # Functional tests
├── test_integration.py                  # Integration tests
├── test_kiv_redirect_fix.py             # KIV redirect fix tests
├── test_kiv_server.py                   # KIV server tests
├── test_kiv_visibility_fix.py           # KIV visibility fix tests
├── test_mark_done_enhanced.py           # Enhanced mark done tests
├── test_mark_done_fix.py                # Mark done fix tests
├── test_modal_close_without_start.py    # Modal close tests
├── test_mode_switching.py               # Mode switching tests
├── test_registration.py                 # Registration tests
├── test_regressions.py                  # Regression tests
├── test_reminder_30_min_interval.py     # Reminder interval tests
├── test_reminder_auto_close.py          # Reminder auto-close tests
├── test_reminder_clear.py               # Reminder clear tests
├── test_reminder_persistence.py         # Reminder persistence tests
├── test_security_updates.py             # Security update tests
├── test_static_files.py                 # Static file tests (15+ tests)
├── test_system_accuracy.py              # System accuracy tests
├── test_terms_and_disclaimer.py         # Terms and disclaimer tests
├── test_user_isolation.py               # User isolation tests
├── test_utility_functions.py            # Utility function tests
├── test_utils.py                        # Test utilities
├── test_work_session_simplified.py      # Simplified work session tests
├── test_work_session_tracking.py        # Work session tracking tests
└── test_workflows.py                    # Workflow tests
```

### Verification Scripts (Python)

```bash
tests/
└── verify_account_deletion_safety.py    # Account deletion safety verification (moved from root)
```

**Purpose:** Verifies critical safety fixes for account deletion including email case sensitivity, deletion window, and cleanup function safeguards.

**Usage:**
```bash
python tests/verify_account_deletion_safety.py
```

**Documentation:** Referenced in `docs/archive/ACCOUNT_DELETION_FIX_COMPLETE.md`

### Validation Scripts (Bash)

```bash
tests/
├── validate_timer_fix.sh                # Timer persistence fix validation (moved from root)
└── TESTING_QUICK_REFERENCE.sh           # Testing strategy quick reference (moved from root)
```

#### validate_timer_fix.sh

**Purpose:** Validates the timer persistence fix by checking JavaScript and Python syntax, and running unit tests.

**Usage:**
```bash
bash tests/validate_timer_fix.sh
```

**Features:**
- JavaScript syntax validation
- Python syntax validation
- Unit test execution for work session tracking
- Detailed validation report

**Documentation:** Referenced in `docs/archive/STATUS_REPORT.md` and `docs/archive/TIMER_PERSISTENCE_IMPLEMENTATION_REPORT.md`

#### TESTING_QUICK_REFERENCE.sh

**Purpose:** Multi-layer testing strategy documentation and quick reference guide.

**Usage:**
```bash
# Display testing strategy guide
./tests/TESTING_QUICK_REFERENCE.sh all
```

**Content:**
- Test layer descriptions (Backend, Frontend, Assets)
- Quick start commands
- Testing workflow phases
- Success criteria
- Best practices

**Documentation:** Referenced in `docs/COMPREHENSIVE_TEST_STRATEGY.md` and `docs/TESTING_STRATEGY_AND_CI_CD.md`

---

## Test Infrastructure Files

```bash
tests/
├── __init__.py                          # Python package marker
├── conftest.py                          # Pytest configuration and fixtures
├── login_fixtures.py                    # Login-related test fixtures
└── run_tests.py                         # Test runner script
```

---

## Test Documentation

```bash
tests/
├── TESTING.md                           # Testing guide
├── TESTING_BEST_PRACTICES.md            # Testing best practices
└── TEST_SUMMARY.md                      # Test summary documentation
```

---

## Running Tests

### Run All Tests

```bash
# From project root
python -m pytest tests/

# Or using the test runner
python tests/run_tests.py
```

### Run Specific Test File

```bash
# Backend tests
python -m pytest tests/test_accurate_comprehensive.py -v

# Frontend tests
python -m pytest tests/test_frontend.py -v

# Specific test
python -m pytest tests/test_checkbox_html_conversion.py -v
```

### Run Test Layers

```bash
# Backend logic tests (9 tests)
python -m pytest tests/test_accurate_comprehensive.py

# Frontend asset tests (20+ tests)
python -m pytest tests/test_frontend_assets.py

# Static file tests (15+ tests)
python -m pytest tests/test_static_files.py
```

---

## Migration Notes

### Files Moved (February 1, 2026)

The following files were moved from the root directory to `tests/` for better organization:

1. **test_checkbox_html_conversion.py** → `tests/test_checkbox_html_conversion.py`
   - Manual test script for checkbox HTML rendering feature
   - Referenced in `docs/archive/CHECKBOX_HTML_RENDERING_IMPLEMENTATION.md`

2. **verify_account_deletion_safety.py** → `tests/verify_account_deletion_safety.py`
   - Verification script for account deletion safety fixes
   - Referenced in `docs/archive/ACCOUNT_DELETION_FIX_COMPLETE.md`

3. **validate_timer_fix.sh** → `tests/validate_timer_fix.sh`
   - Validation script for timer persistence fix
   - Updated to use relative paths from script directory
   - Referenced in `docs/archive/STATUS_REPORT.md` and `docs/archive/TIMER_PERSISTENCE_IMPLEMENTATION_REPORT.md`

4. **TESTING_QUICK_REFERENCE.sh** → `tests/TESTING_QUICK_REFERENCE.sh`
   - Testing strategy quick reference guide
   - Updated self-references to new path
   - Referenced in `docs/COMPREHENSIVE_TEST_STRATEGY.md` and `docs/TESTING_STRATEGY_AND_CI_CD.md`

### Updated References

All documentation files were updated to reflect the new paths:
- `docs/archive/CHECKBOX_HTML_RENDERING_IMPLEMENTATION.md`
- `docs/archive/ACCOUNT_DELETION_FIX_COMPLETE.md`
- `docs/archive/STATUS_REPORT.md`
- `docs/archive/TIMER_PERSISTENCE_IMPLEMENTATION_REPORT.md`
- `docs/COMPREHENSIVE_TEST_STRATEGY.md`
- `docs/TESTING_STRATEGY_AND_CI_CD.md`

---

## Best Practices

### File Naming Conventions

1. **Test files:** Start with `test_` prefix (e.g., `test_feature.py`)
2. **Verification scripts:** Start with `verify_` prefix (e.g., `verify_safety.py`)
3. **Validation scripts:** Start with `validate_` prefix (e.g., `validate_fix.sh`)
4. **Reference guides:** Use descriptive names in CAPS (e.g., `TESTING_QUICK_REFERENCE.sh`)

### Directory Organization

```bash
tests/
├── *.py                  # All test files
├── *.sh                  # Shell scripts for testing/validation
├── *.md                  # Test documentation
├── conftest.py           # Pytest configuration
└── fixtures/             # Future: Test fixtures (if needed)
```

### Adding New Tests

1. Create test file in `tests/` directory with `test_` prefix
2. Follow existing test patterns and conventions
3. Add documentation in test docstrings
4. Update test summary documentation if needed
5. Ensure tests pass before committing

---

## Related Documentation

- **[COMPREHENSIVE_TEST_STRATEGY.md](COMPREHENSIVE_TEST_STRATEGY.md)** - Complete testing strategy
- **[TESTING_STRATEGY_AND_CI_CD.md](TESTING_STRATEGY_AND_CI_CD.md)** - CI/CD and testing workflow
- **[tests/TESTING.md](../tests/TESTING.md)** - Testing guide
- **[tests/TESTING_BEST_PRACTICES.md](../tests/TESTING_BEST_PRACTICES.md)** - Testing best practices
- **[tests/TEST_SUMMARY.md](../tests/TEST_SUMMARY.md)** - Test summary

---

Last Updated: February 1, 2026  
Status: COMPLETE ✅
