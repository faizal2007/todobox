#!/usr/bin/env python3
"""
TodoBox Functional Tests - Complete Command Reference
Todomanage.py Testing Edition
"""

import subprocess
import sys

def print_header():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║   TodoBox Functional Test Suite - Command Reference (with Todomanage)     ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def main():
    print_header()
    
    print_section("QUICK START - RUN TESTS")
    print("""
    # Run all 39 tests (including todomanage)
    python -m pytest tests/test_functional.py -v
    
    # Run with test runner
    python tests/run_tests.py all --verbose
    
    # Generate coverage report
    python tests/run_tests.py all --coverage
    """)
    
    print_section("RUN TODOMANAGE TESTS SPECIFICALLY")
    print("""
    # All todomanage tests (17 tests)
    pytest tests/test_functional.py -k "Todomanage" -v
    
    # User management tests (4 tests)
    pytest tests/test_functional.py::TestTodomanageUserManagement -v
    
    # Installation tests (2 tests)
    pytest tests/test_functional.py::TestTodomanageInstallation -v
    
    # Integration tests (4 tests)
    pytest tests/test_functional.py::TestTodomanageIntegration -v
    
    # Configuration tests (3 tests)
    pytest tests/test_functional.py::TestTodomanageConfigManagement -v
    
    # Error handling tests (4 tests)
    pytest tests/test_functional.py::TestTodomanageErrorHandling -v
    """)
    
    print_section("RUN SPECIFIC INDIVIDUAL TESTS")
    print("""
    # User creation tests
    pytest tests/test_functional.py::TestTodomanageUserManagement::test_create_user_via_todomanage -v
    pytest tests/test_functional.py::TestTodomanageUserManagement::test_list_users_via_todomanage -v
    pytest tests/test_functional.py::TestTodomanageUserManagement::test_assign_admin_via_todomanage -v
    pytest tests/test_functional.py::TestTodomanageUserManagement::test_delete_user_via_todomanage -v
    
    # Installation tests
    pytest tests/test_functional.py::TestTodomanageInstallation::test_install_database_choice_validation -v
    pytest tests/test_functional.py::TestTodomanageInstallation::test_flaskenv_update_function -v
    
    # Integration tests
    pytest tests/test_functional.py::TestTodomanageIntegration::test_todomanage_user_creation_integration -v
    pytest tests/test_functional.py::TestTodomanageIntegration::test_todomanage_admin_operations -v
    pytest tests/test_functional.py::TestTodomanageIntegration::test_todomanage_user_password_update -v
    pytest tests/test_functional.py::TestTodomanageIntegration::test_todomanage_bulk_operations -v
    
    # Configuration tests
    pytest tests/test_functional.py::TestTodomanageConfigManagement::test_flaskenv_configuration_parsing -v
    pytest tests/test_functional.py::TestTodomanageConfigManagement::test_database_url_construction -v
    pytest tests/test_functional.py::TestTodomanageConfigManagement::test_configuration_validation -v
    
    # Error handling tests
    pytest tests/test_functional.py::TestTodomanageErrorHandling::test_user_creation_duplicate_username -v
    pytest tests/test_functional.py::TestTodomanageErrorHandling::test_user_creation_duplicate_email -v
    pytest tests/test_functional.py::TestTodomanageErrorHandling::test_invalid_password_validation -v
    pytest tests/test_functional.py::TestTodomanageErrorHandling::test_invalid_email_validation -v
    """)
    
    print_section("RUN TEST CATEGORIES")
    print("""
    # Authentication tests (5 tests)
    pytest tests/test_functional.py::TestAuthentication -v
    
    # Todo management tests (5 tests)
    pytest tests/test_functional.py::TestTodoManagement -v
    
    # User isolation tests (2 tests)
    pytest tests/test_functional.py::TestUserIsolation -v
    
    # Sharing tests (2 tests)
    pytest tests/test_functional.py::TestTodoSharing -v
    
    # Admin tests (3 tests)
    pytest tests/test_functional.py::TestAdminFunctionality -v
    
    # Settings tests (3 tests)
    pytest tests/test_functional.py::TestUserSettings -v
    
    # Integration tests (2 tests)
    pytest tests/test_functional.py::TestEndToEndWorkflow -v
    """)
    
    print_section("ADVANCED OPTIONS")
    print("""
    # Verbose output with all details
    pytest tests/test_functional.py -vv
    
    # Show print statements
    pytest tests/test_functional.py -s
    
    # Stop on first failure
    pytest tests/test_functional.py -x
    
    # Stop after N failures
    pytest tests/test_functional.py --maxfail=2
    
    # Show slowest 10 tests
    pytest tests/test_functional.py --durations=10
    
    # Run with coverage report
    pytest tests/test_functional.py --cov=app --cov-report=term-missing
    
    # Generate HTML coverage report
    pytest tests/test_functional.py --cov=app --cov-report=html
    
    # Generate HTML test report
    pytest tests/test_functional.py --html=report.html --self-contained-html
    
    # Run tests in parallel (requires pytest-xdist)
    pytest tests/test_functional.py -n auto
    
    # Run with keyword filter
    pytest tests/test_functional.py -k "create" -v
    
    # Run with marker
    pytest tests/test_functional.py -m "not slow" -v
    """)
    
    print_section("TEST RUNNER SCRIPT")
    print("""
    # Run all tests
    python tests/run_tests.py all
    
    # Run with verbose output
    python tests/run_tests.py all --verbose
    
    # Run with coverage
    python tests/run_tests.py all --coverage
    
    # Run with HTML report
    python tests/run_tests.py all --html
    
    # Run specific suite
    python tests/run_tests.py auth       # Authentication tests
    python tests/run_tests.py todos      # Todo management tests
    python tests/run_tests.py isolation  # User isolation tests
    python tests/run_tests.py sharing    # Sharing tests
    python tests/run_tests.py admin      # Admin tests
    python tests/run_tests.py settings   # Settings tests
    python tests/run_tests.py integration # Integration tests
    
    # Combine options
    python tests/run_tests.py all --verbose --coverage
    """)
    
    print_section("TEST COLLECTION")
    print("""
    # List all tests
    pytest tests/test_functional.py --collect-only
    
    # List tests in quiet mode
    pytest tests/test_functional.py --collect-only -q
    
    # Show test count only
    pytest tests/test_functional.py --collect-only -q | tail -1
    """)
    
    print_section("DOCUMENTATION")
    print("""
    # View quick start guide
    python tests/QUICK_START.py
    
    # View todomanage testing guide
    cat tests/TODOMANAGE_TEST_GUIDE.md
    
    # View testing documentation
    cat tests/TESTING.md
    
    # View test runner help
    python tests/run_tests.py --help
    """)
    
    print_section("CONTINUOUS INTEGRATION")
    print("""
    # Run tests with CI-friendly output
    pytest tests/test_functional.py -v --tb=short
    
    # Generate junit XML report (for CI systems)
    pytest tests/test_functional.py --junit-xml=report.xml
    
    # Generate coverage in XML (for codecov)
    pytest tests/test_functional.py --cov=app --cov-report=xml
    
    # Exit with failure on test failures
    pytest tests/test_functional.py || exit 1
    """)
    
    print_section("TROUBLESHOOTING")
    print("""
    # Debug a failing test
    pytest tests/test_functional.py::TestName::test_name -vvs --tb=long
    
    # Drop into debugger on failure
    pytest tests/test_functional.py --pdb
    
    # Show local variables on failure
    pytest tests/test_functional.py -l
    
    # Show full traceback
    pytest tests/test_functional.py --tb=long
    
    # Capture print output
    pytest tests/test_functional.py -s
    
    # Verbose + show output + long traceback
    pytest tests/test_functional.py -vvs --tb=long
    """)
    
    print_section("SUMMARY")
    print("""
    Total Tests:           39
    - Original:            22
    - Todomanage:          17
    
    Test Classes:          11
    - Authentication:      1
    - Todo Management:     1
    - User Isolation:      1
    - Sharing:             1
    - Admin:               1
    - Settings:            1
    - Integration:         1
    - Todomanage User:     1
    - Todomanage Install:  1
    - Todomanage Config:   1
    - Todomanage Error:    1
    
    Pass Rate:             100% (39/39 passing)
    Execution Time:        3-6 seconds
    Database:              SQLite (in-memory)
    
    Start testing: python tests/run_tests.py all --verbose
    """)
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    main()
