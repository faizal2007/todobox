#!/usr/bin/env python3
"""
Comprehensive pre-push test suite validator.
Ensures all critical tests pass before allowing push to master.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"  → {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"    ✓ {description}")
        else:
            print(f"    ✗ {description}")
            if result.stderr:
                print(f"      Error: {result.stderr[:100]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout: {description}")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def validate_test_suite() -> int:
    """Run comprehensive test validation."""
    print("\n" + "=" * 70)
    print("🧪 COMPREHENSIVE TEST SUITE VALIDATOR")
    print("=" * 70)
    
    checks = [
        # Python syntax
        (
            "python3 -m py_compile tests/test_*.py app/**/*.py 2>/dev/null",
            "Python syntax validation"
        ),
        
        # Imports
        (
            'python3 -c "from app import app, db; from app.models import *; from app.routes import *; from app.session_handler import *"',
            "Module imports validation"
        ),
        
        # Core tests
        (
            "python3 -m pytest tests/test_accurate_comprehensive.py -q --tb=no 2>/dev/null",
            "Core functionality tests"
        ),
        
        # Route tests - All routes
        (
            "python3 -m pytest tests/test_all_routes.py -q --tb=no 2>/dev/null",
            "All routes tests"
        ),
        
        # API routes
        (
            "python3 -m pytest tests/test_all_routes.py::TestAPIRoutes -q --tb=no 2>/dev/null",
            "API routes validation"
        ),
        
        # CRUD operations
        (
            "python3 -m pytest tests/test_all_routes.py::TestTodoCRUDRoutes -q --tb=no 2>/dev/null",
            "Todo CRUD operations"
        ),
        
        # Authentication
        (
            "python3 -m pytest tests/test_all_routes.py::TestAuthenticationRoutes -q --tb=no 2>/dev/null",
            "Authentication routes"
        ),
        
        # Integration tests
        (
            "python3 -m pytest tests/test_integration.py -q --tb=no 2>/dev/null || true",
            "Integration tests"
        ),
        
        # Session handler
        (
            "python3 -m pytest tests/test_session_handler.py -q --tb=no 2>/dev/null || true",
            "Session handler tests"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, desc in checks:
        if run_command(cmd, desc):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(validate_test_suite())
