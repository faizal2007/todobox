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
        description='Run TodoBox functional tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py all              Run all tests
  python test_runner.py auth             Run authentication tests
  python test_runner.py todos            Run todo management tests
  python test_runner.py --verbose        Run with verbose output
  python test_runner.py --coverage       Run with coverage report
        """
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['all', 'auth', 'todos', 'isolation', 'sharing', 'admin', 'settings', 'integration'],
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
    
    # Build pytest command as a list (safer than shell=True)
    test_file = 'tests/test_functional.py'
    cmd = ['python', '-m', 'pytest', test_file]
    
    # Add test suite selection
    suite_map = {
        'all': '',
        'auth': '::TestAuthentication',
        'todos': '::TestTodoManagement',
        'isolation': '::TestUserIsolation',
        'sharing': '::TestTodoSharing',
        'admin': '::TestAdminFunctionality',
        'settings': '::TestUserSettings',
        'integration': '::TestEndToEndWorkflow'
    }
    
    if args.suite != 'all':
        # Replace the test file with the file + test class selector
        cmd[cmd.index(test_file)] = test_file + suite_map[args.suite]
    
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
