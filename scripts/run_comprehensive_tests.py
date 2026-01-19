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
    print(f"\n  → {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    ❌ Timeout: {description}")
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def validate_test_suite() -> int:
    """Run comprehensive test validation."""
    print("=" * 60)
    print("🧪 COMPREHENSIVE TEST SUITE VALIDATOR")
    print("=" * 60)
    
    checks = [
        # Python syntax
        (
            "python -m py_compile app/**/*.py 2>/dev/null",
            "Python syntax validation"
        ),
        
        # Imports
        (
            'python -c "from app import app, db; from app.models import *; from app.routes import *"',
            "Module imports validation"
        ),
        
        # Core tests
        (
            "python -m pytest tests/test_accurate_comprehensive.py -q --tb=no",
            "Core functionality tests"
        ),
        
        # Route tests
        (
            "python -m pytest tests/test_all_routes.py::TestAPIRoutes -q --tb=no",
            "API routes validation"
        ),
        
        # CRUD operations
        (
            "python -m pytest tests/test_all_routes.py::TestTodoCRUDRoutes -q --tb=no",
            "Todo CRUD operations"
        ),
        
        # Authentication
        (
            "python -m pytest tests/test_all_routes.py::TestAuthenticationRoutes -q --tb=no",
            "Authentication routes"
        ),
        
        # Integration tests
        (
            "python -m pytest tests/test_integration.py -q --tb=no 2>/dev/null || true",
            "Integration tests (optional)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, desc in checks:
        if run_command(cmd, desc):
            print(f"    ✓ {desc}")
            passed += 1
        else:
            print(f"    ✗ {desc}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(validate_test_suite())
