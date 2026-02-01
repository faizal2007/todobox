#!/usr/bin/env python3
"""
Main test runner for TodoBox project.
Provides convenient shortcuts to run test suites.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_tests(suite: str, verbose: bool = False, coverage: bool = False, keyword: str = None) -> int:
    """Run tests using the tests/run_tests.py script."""
    cmd = ['python3', 'tests/run_tests.py', suite]
    
    if verbose:
        cmd.append('-v')
    if coverage:
        cmd.append('-c')
    if keyword:
        cmd.extend(['-k', keyword])
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(
        description='TodoBox Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py              Run all tests
  python test.py routes       Run route tests only
  python test.py core         Run core functionality tests
  python test.py -v           Run with verbose output
  python test.py -c           Run with coverage report
  python test.py -k keyword   Run tests matching keyword
  python test.py --quick      Run quick validation
        """
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['all', 'routes', 'core', 'features', 'auth', 'todos', 'integration', 'quick'],
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
    
    args = parser.parse_args()
    
    # Handle 'quick' suite - run comprehensive validator instead
    if args.suite == 'quick':
        print("\n🚀 Running quick validation suite...\n")
        result = subprocess.run(['python3', 'scripts/run_comprehensive_tests.py'])
        return result.returncode
    
    # Run normal test suite
    return run_tests(args.suite, args.verbose, args.coverage, args.keyword)

if __name__ == '__main__':
    sys.exit(main())
