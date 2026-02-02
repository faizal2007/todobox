#!/usr/bin/env python3
"""
Test Runner for TodoBox Functional Tests
Provides convenient commands to run test suites with various configurations.
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd_list, description=""):
    """Run a command and return exit code.
    
    Args:
        cmd_list: List of command arguments (e.g., ['python', '-m', 'pytest'])
        description: Optional description to print before running
    """
    if description:
        print(f"\n{'='*70}")
        print(f"  {description}")
        print(f"{'='*70}\n")
    
    result = subprocess.run(cmd_list, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description='Run TodoBox test suites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py all              Run all tests
  python run_tests.py routes           Run all route tests
  python run_tests.py core             Run core functionality tests
  python run_tests.py features         Run feature tests
  python run_tests.py --verbose        Run with verbose output
  python run_tests.py --coverage       Run with coverage report
        """
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['all', 'routes', 'core', 'features', 'auth', 'todos', 'integration'],
        help='Test suite to run (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '-k', '--keyword',
        help='Run tests matching keyword'
    )
    parser.add_argument(
        '--pdb',
        action='store_true',
        help='Drop into debugger on failures'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML report'
    )
    
    args = parser.parse_args()
    
    # Build pytest command - run appropriate test files based on suite
    suite_map = {
        'all': ['tests/test_all_routes.py', 'tests/test_accurate_comprehensive.py', 'tests/test_integration.py'],
        'routes': ['tests/test_all_routes.py'],
        'core': ['tests/test_accurate_comprehensive.py'],
        'features': ['tests/test_achievements.py', 'tests/test_backup.py', 'tests/test_registration.py'],
        'auth': ['tests/test_all_routes.py::TestAuthenticationRoutes'],
        'todos': ['tests/test_all_routes.py::TestTodoCRUDRoutes'],
        'integration': ['tests/test_integration.py'],
    }
    
    test_targets = suite_map.get(args.suite, suite_map['all'])
    cmd = ['python', '-m', 'pytest'] + test_targets
    
    # Add flags
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')
    
    if args.coverage:
        cmd.extend(['--cov=app', '--cov-report=term-missing', '--cov-report=html'])
    
    if args.keyword:
        cmd.extend(['-k', args.keyword])
    
    if args.pdb:
        cmd.append('--pdb')
    
    if args.html:
        cmd.extend(['--html=report.html', '--self-contained-html'])
    
    # Show what we're running
    print(f"\n{'='*70}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print(f"\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
