#!/usr/bin/env python3
"""
Identify obsolete test files that can be removed
"""

# Obsolete test files (reasons below)
obsolete_tests = {
    # FIX-SPECIFIC TESTS (functionality now integrated into main test suites)
    'test_mark_done_fix.py': 'Specific fix - functionality in test_all_routes.py',
    'test_mark_done_enhanced.py': 'Enhanced version - superseded by test_all_routes.py',
    'test_modal_close_without_start.py': 'Specific bug fix - covered by test_all_routes.py',
    'test_kiv_redirect_fix.py': 'Specific bug fix - covered by test_all_routes.py',
    'test_kiv_visibility_fix.py': 'Specific bug fix - covered by test_all_routes.py',
    'test_deleted_account_block.py': 'Specific feature - covered by test_all_routes.py',
    'test_cooldown_expiry.py': 'Reminder feature - covered by test_accurate_comprehensive.py',
    'test_reminder_30_min_interval.py': 'Specific reminder interval - superseded',
    'test_reminder_auto_close.py': 'Auto-close feature - covered in comprehensive tests',
    'test_reminder_clear.py': 'Reminder clear - covered in comprehensive tests',
    
    # DUPLICATE/REDUNDANT TEST SUITES
    'test_comprehensive.py': 'Duplicates test_all_routes.py and test_accurate_comprehensive.py',
    'test_functional.py': 'Duplicates test_all_routes.py (also broken - referenced by run_tests.py)',
    'test_backend_routes.py': 'Duplicates test_all_routes.py routes',
    'test_frontend.py': 'Duplicates test_frontend_assets.py',
    'test_features_comprehensive.py': 'Manual test - superseded by automated tests',
    'test_system_accuracy.py': 'Superseded by test_accurate_comprehensive.py',
    
    # EMAIL TESTS (manual/specific - can be kept or removed)
    'test_email_direct.py': 'Direct email test - specific verification',
    'test_email_headers.py': 'Specific email headers - can be removed',
    'test_email_send.py': 'Direct email send - can be removed',
    
    # UTILITY TESTS (small/specific)
    'test_checkbox_html_conversion.py': 'Specific feature - small test',
    
    # WORKFLOW TESTS (can be removed or kept)
    'test_workflows.py': 'Manual workflow test',
    'test_work_session_simplified.py': 'Simplified version - superseded by test_work_session_tracking.py',
}

# Core test files to keep
core_tests = [
    'test_all_routes.py',              # PRIMARY: All route tests
    'test_accurate_comprehensive.py',  # PRIMARY: Core functionality
    'test_all_routes.py',              # API endpoints, CRUD, auth
    'test_achievements.py',            # Feature tests
    'test_achievements_time_calculation.py',  # Feature tests
    'test_achievement_modal_endpoint.py',  # Feature tests
    'test_backup.py',                  # Backup feature
    'test_terms_and_disclaimer.py',    # Terms feature
    'test_registration.py',            # Registration flow
    'test_regressions.py',             # Regression tests
    'test_integration.py',             # Integration tests
    'test_security_updates.py',        # Security tests
    'test_user_isolation.py',          # User isolation/security
    'test_utility_functions.py',       # Utility functions
    'test_utils.py',                   # Utils
    'test_frontend_assets.py',         # Frontend assets
    'test_static_files.py',            # Static files
    'test_kiv_server.py',              # KIV feature
    'test_mode_switching.py',          # Mode switching feature
    'test_reminder_persistence.py',    # Reminder persistence
    'test_session_handler.py',         # Session expiration (new)
]

print("\nOBSOLETE TEST FILES TO REMOVE:")
print("=" * 80)
for test_file, reason in sorted(obsolete_tests.items()):
    print(f"  ✗ {test_file:<40} - {reason}")

print(f"\n\nCORE TEST FILES TO KEEP:")
print("=" * 80)
for test_file in sorted(core_tests):
    print(f"  ✓ {test_file}")

print(f"\n\nSummary:")
print(f"  Obsolete files: {len(obsolete_tests)}")
print(f"  Core files: {len(core_tests)}")
print(f"  Reduction: {len(obsolete_tests) / (len(obsolete_tests) + len(core_tests)) * 100:.1f}%")
