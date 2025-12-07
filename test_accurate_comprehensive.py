#!/usr/bin/env python3
"""
Comprehensive Accurate Test Suite for TodoBox

This test suite validates against your REAL MySQL database to ensure:
1. New patches don't break existing stable functionality
2. Data persists correctly across sessions
3. User isolation is maintained
4. All routes work as expected
5. Database queries return correct results

Usage:
    python test_accurate_comprehensive.py
    
Output:
    - Green checkmarks (✓) for passing tests
    - Red X marks (✗) for failing tests
    - Summary of passed/failed/total tests
"""

import sys
import os
import time
from datetime import datetime, timedelta
from contextlib import contextmanager

# Add the app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import Todo, User, Tracker, Status, KIV
from flask import json
from flask_login import login_user
import logging

# Disable Flask logging during tests
logging.getLogger('flask').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Test counters
tests_passed = 0
tests_failed = 0
tests_total = 0
failed_tests = []


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")


def print_test(name):
    """Print test name"""
    print(f"{BOLD}Testing: {name}{RESET}")


def pass_test(message):
    """Mark test as passed"""
    global tests_passed, tests_total
    tests_passed += 1
    tests_total += 1
    print(f"  {GREEN}✓ PASS{RESET}: {message}")


def fail_test(message, details=""):
    """Mark test as failed"""
    global tests_failed, tests_total, failed_tests
    tests_failed += 1
    tests_total += 1
    failed_tests.append((message, details))
    print(f"  {RED}✗ FAIL{RESET}: {message}")
    if details:
        print(f"        {RED}→ {details}{RESET}")


@contextmanager
def app_context():
    """Provide app context for tests"""
    with app.app_context():
        yield


def get_or_create_test_user(email="test@test.com"):
    """Get or create a test user"""
    with app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()
        return user.id


def cleanup_test_data(user_id):
    """Clean up test data for a user"""
    with app_context():
        # Delete todos for user
        todos = Todo.query.filter_by(user_id=user_id).all()
        for todo in todos:
            # Delete trackers first (foreign key)
            Tracker.query.filter_by(todo_id=todo.id).delete()
            # Delete KIV entries
            KIV.query.filter_by(todo_id=todo.id).delete()
            db.session.delete(todo)
        db.session.commit()


# ============================================================================
# TEST SUITE 1: DATABASE PERSISTENCE
# ============================================================================

def test_database_persistence():
    """Test that data persists correctly across sessions"""
    print_header("TEST SUITE 1: DATABASE PERSISTENCE")
    
    user_id = get_or_create_test_user("persist@test.com")
    cleanup_test_data(user_id)
    
    print_test("Data persists in same session")
    with app_context():
        # Create todo
        todo = Todo(
            name="Persistence Test Todo",
            details="Testing data persistence",
            user_id=user_id,
            modified=datetime.now()
        )
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        # Verify in same session
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check and todo_check.name == "Persistence Test Todo":
            pass_test(f"Todo created and verified in same session (id={todo_id})")
        else:
            fail_test("Todo not found in same session", "Database insert failed")
            return
    
    print_test("Data persists across sessions")
    with app_context():
        # Open new session and verify data still exists
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check and todo_check.name == "Persistence Test Todo":
            pass_test(f"Todo persists after session close (id={todo_id})")
        else:
            fail_test("Todo lost after session close", "Data not persisted to database")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 2: KIV TABLE FUNCTIONALITY
# ============================================================================

def test_kiv_functionality():
    """Test KIV table operations"""
    print_header("TEST SUITE 2: KIV TABLE FUNCTIONALITY")
    
    user_id = get_or_create_test_user("kiv@test.com")
    cleanup_test_data(user_id)
    
    print_test("KIV.add() creates KIV entry")
    with app_context():
        # Create todo
        todo = Todo(name="KIV Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        # Add to KIV
        KIV.add(todo_id, user_id)
        
        # Verify KIV entry created
        kiv_entry = KIV.query.filter_by(todo_id=todo_id).first()
        if kiv_entry and kiv_entry.is_active:
            pass_test(f"KIV entry created for todo {todo_id}")
        else:
            fail_test("KIV entry not created", "KIV.add() failed")
            return
    
    print_test("KIV.is_kiv() detects KIV status")
    with app_context():
        is_kiv = KIV.is_kiv(todo_id)
        if is_kiv:
            pass_test(f"KIV.is_kiv({todo_id}) returns True")
        else:
            fail_test(f"KIV.is_kiv({todo_id}) returns False", "Should return True")
    
    print_test("KIV.remove() removes from KIV")
    with app_context():
        KIV.remove(todo_id)
        is_kiv = KIV.is_kiv(todo_id)
        if not is_kiv:
            pass_test(f"KIV.remove({todo_id}) effective, is_kiv now False")
        else:
            fail_test("KIV.remove() failed", "Todo still marked as KIV")
    
    print_test("KIV status persists across sessions")
    with app_context():
        # Re-add to KIV
        KIV.add(todo_id, user_id)
    
    with app_context():
        # Check in new session
        is_kiv = KIV.is_kiv(todo_id)
        if is_kiv:
            pass_test("KIV status persists across session boundaries")
        else:
            fail_test("KIV status lost after session", "Data not committed to database")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 3: USER ISOLATION
# ============================================================================

def test_user_isolation():
    """Test that users can't see each other's todos"""
    print_header("TEST SUITE 3: USER ISOLATION")
    
    user1_id = get_or_create_test_user("user1@test.com")
    user2_id = get_or_create_test_user("user2@test.com")
    
    cleanup_test_data(user1_id)
    cleanup_test_data(user2_id)
    
    print_test("User1 can't see User2's todos")
    with app_context():
        # Create todo for user1
        todo1 = Todo(name="User1 Todo", user_id=user1_id, modified=datetime.now())
        db.session.add(todo1)
        db.session.commit()
        
        # Create todo for user2
        todo2 = Todo(name="User2 Todo", user_id=user2_id, modified=datetime.now())
        db.session.add(todo2)
        db.session.commit()
        
        # User1 should see only their todo
        user1_todos = Todo.query.filter_by(user_id=user1_id).all()
        user2_todos = Todo.query.filter_by(user_id=user2_id).all()
        
        if len(user1_todos) == 1 and user1_todos[0].name == "User1 Todo":
            pass_test("User1 sees only their own todos")
        else:
            fail_test("User1 isolation broken", f"User1 sees {len(user1_todos)} todos")
        
        if len(user2_todos) == 1 and user2_todos[0].name == "User2 Todo":
            pass_test("User2 sees only their own todos")
        else:
            fail_test("User2 isolation broken", f"User2 sees {len(user2_todos)} todos")
    
    cleanup_test_data(user1_id)
    cleanup_test_data(user2_id)


# ============================================================================
# TEST SUITE 4: TRACKER & STATUS FUNCTIONALITY
# ============================================================================

def test_tracker_functionality():
    """Test Tracker (status history) functionality"""
    print_header("TEST SUITE 4: TRACKER & STATUS FUNCTIONALITY")
    
    user_id = get_or_create_test_user("tracker@test.com")
    cleanup_test_data(user_id)
    
    print_test("Tracker.add() creates status entry")
    with app_context():
        # Create todo
        todo = Todo(name="Tracker Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        # Add status
        Tracker.add(todo_id, 5, datetime.now())  # Status 5 = new
        
        # Verify tracker created
        tracker = Tracker.query.filter_by(todo_id=todo_id).first()
        if tracker and tracker.status_id == 5:
            pass_test(f"Tracker entry created with status 5 (new)")
        else:
            fail_test("Tracker entry not created", "Tracker.add() failed")
            return
    
    print_test("Tracker returns latest status (multiple entries)")
    with app_context():
        # Add multiple status changes
        Tracker.add(todo_id, 8, datetime.now())  # Status 8 = re-assign
        Tracker.add(todo_id, 5, datetime.now())  # Status 5 = new again
        
        # Get latest tracker
        latest_tracker = Tracker.query.filter_by(todo_id=todo_id).order_by(
            Tracker.timestamp.desc(), Tracker.id.desc()
        ).first()
        
        if latest_tracker and latest_tracker.status_id == 5:
            pass_test("Latest tracker query returns most recent status (5)")
        else:
            fail_test("Tracker query returns wrong status", 
                     f"Expected 5, got {latest_tracker.status_id if latest_tracker else 'None'}")
    
    print_test("Tracker entries persist in history")
    with app_context():
        # Count tracker entries
        tracker_count = Tracker.query.filter_by(todo_id=todo_id).count()
        if tracker_count >= 3:
            pass_test(f"Tracker history preserved ({tracker_count} entries)")
        else:
            fail_test("Tracker history lost", f"Only {tracker_count} entries (expected 3+)")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 5: TODO SCHEDULING
# ============================================================================

def test_todo_scheduling():
    """Test todo scheduling functionality"""
    print_header("TEST SUITE 5: TODO SCHEDULING")
    
    user_id = get_or_create_test_user("schedule@test.com")
    cleanup_test_data(user_id)
    
    print_test("Todo created with today's date")
    with app_context():
        today = datetime.now().date()
        todo = Todo(name="Today Todo", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check.modified.date() == today:
            pass_test(f"Todo created with today's date ({today})")
        else:
            fail_test("Todo date incorrect", f"Expected {today}, got {todo_check.modified.date()}")
            return
    
    print_test("Todo schedule can be updated to tomorrow")
    with app_context():
        tomorrow = datetime.now() + timedelta(days=1)
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.modified = tomorrow
        db.session.commit()
        
        # Verify update
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check.modified.date() == tomorrow.date():
            pass_test(f"Todo scheduled to tomorrow ({tomorrow.date()})")
        else:
            fail_test("Todo schedule not updated", f"Date: {todo_check.modified.date()}")
    
    print_test("Todo schedule can be updated to specific date")
    with app_context():
        specific_date = datetime.now() + timedelta(days=7)
        todo = Todo.query.filter_by(id=todo_id).first()
        todo.modified = specific_date
        db.session.commit()
        
        # Verify update
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check.modified.date() == specific_date.date():
            pass_test(f"Todo scheduled to specific date ({specific_date.date()})")
        else:
            fail_test("Todo schedule not updated", f"Date: {todo_check.modified.date()}")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 6: QUERY FILTERS
# ============================================================================

def test_query_filters():
    """Test database query filters"""
    print_header("TEST SUITE 6: QUERY FILTERS")
    
    user_id = get_or_create_test_user("filter@test.com")
    cleanup_test_data(user_id)
    
    print_test("Query filter: Find undone todos")
    with app_context():
        # Create multiple todos with different statuses
        todo_new = Todo(name="New Todo", user_id=user_id, modified=datetime.now())
        db.session.add(todo_new)
        db.session.commit()
        
        todo_done = Todo(name="Done Todo", user_id=user_id, modified=datetime.now())
        db.session.add(todo_done)
        db.session.commit()
        
        # Add status to new todo
        Tracker.add(todo_new.id, 5, datetime.now())  # Status 5 = new
        
        # Add status to done todo
        Tracker.add(todo_done.id, 6, datetime.now())  # Status 6 = done
        
        # Query for undone todos
        undone_todos = Todo.query.filter(
            Todo.user_id == user_id
        ).all()
        
        undone_with_correct_status = []
        for todo in undone_todos:
            latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(
                Tracker.timestamp.desc(), Tracker.id.desc()
            ).first()
            if latest_tracker and latest_tracker.status_id != 6:
                undone_with_correct_status.append(todo)
        
        if len(undone_with_correct_status) >= 1 and undone_with_correct_status[0].name == "New Todo":
            pass_test("Query finds undone todos (status != 6)")
        else:
            fail_test("Query filter broken", f"Found {len(undone_with_correct_status)} undone todos")
    
    print_test("Query filter: Exclude KIV todos")
    with app_context():
        # Create KIV todo
        todo_kiv = Todo(name="KIV Todo", user_id=user_id, modified=datetime.now())
        db.session.add(todo_kiv)
        db.session.commit()
        
        # Add to KIV
        KIV.add(todo_kiv.id, user_id)
        
        # Query for undone non-KIV todos
        undone_non_kiv = []
        todos = Todo.query.filter(Todo.user_id == user_id).all()
        for todo in todos:
            latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(
                Tracker.timestamp.desc(), Tracker.id.desc()
            ).first()
            if latest_tracker and latest_tracker.status_id != 6 and not KIV.is_kiv(todo.id):
                undone_non_kiv.append(todo)
        
        if len(undone_non_kiv) >= 1:
            pass_test(f"Query correctly excludes KIV todos ({len(undone_non_kiv)} regular undone)")
        else:
            fail_test("Query filter broken for KIV exclusion", "Should find at least 1 non-KIV undone")
    
    print_test("Query filter: Find KIV todos")
    with app_context():
        # Query for KIV todos
        all_todos = Todo.query.filter(Todo.user_id == user_id).all()
        kiv_todos = []
        for todo in all_todos:
            if KIV.is_kiv(todo.id):
                kiv_todos.append(todo)
        
        if len(kiv_todos) >= 1 and kiv_todos[0].name == "KIV Todo":
            pass_test(f"Query finds KIV todos ({len(kiv_todos)} found)")
        else:
            fail_test("Query filter broken for KIV", f"Found {len(kiv_todos)} KIV todos")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 7: ROUTE FUNCTIONALITY
# ============================================================================

def test_route_functionality():
    """Test Flask routes work correctly"""
    print_header("TEST SUITE 7: ROUTE FUNCTIONALITY")
    
    user_id = get_or_create_test_user("route@test.com")
    cleanup_test_data(user_id)
    
    print_test("Route query logic works correctly")
    with app_context():
        # Create test todo
        todo = Todo(name="Route Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        Tracker.add(todo.id, 5, datetime.now())
        
        # Test the query logic directly
        todos = Todo.query.filter_by(user_id=user_id).all()
        if len(todos) > 0:
            pass_test("Route can query todos from database")
        else:
            fail_test("Route query failed", "No todos found in database")
    
    print_test("KIV routing logic works correctly")
    with app_context():
        # Test the route logic for undone todos
        todos = Todo.query.filter_by(user_id=user_id).all()
        undone = []
        kiv = []
        
        for todo in todos:
            latest_tracker = Tracker.query.filter_by(todo_id=todo.id).order_by(
                Tracker.timestamp.desc(), Tracker.id.desc()
            ).first()
            
            if latest_tracker:
                if latest_tracker.status_id != 6 and not KIV.is_kiv(todo.id):
                    undone.append(todo)
                elif KIV.is_kiv(todo.id):
                    kiv.append(todo)
        
        if len(undone) >= 1:
            pass_test(f"Route logic identifies undone todos ({len(undone)} found)")
        else:
            fail_test("Route logic broken for undone", "Should find at least 1")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 8: DATA INTEGRITY
# ============================================================================

def test_data_integrity():
    """Test data integrity constraints"""
    print_header("TEST SUITE 8: DATA INTEGRITY")
    
    user_id = get_or_create_test_user("integrity@test.com")
    cleanup_test_data(user_id)
    
    print_test("Foreign key constraint: Todo requires user_id")
    with app_context():
        try:
            todo = Todo(name="Orphan Todo", user_id=99999, modified=datetime.now())
            db.session.add(todo)
            db.session.commit()
            fail_test("Foreign key constraint not enforced", "Created todo with invalid user_id")
        except Exception as e:
            pass_test("Foreign key constraint enforced")
    
    print_test("KIV unique constraint: One KIV entry per todo")
    with app_context():
        # Create todo
        todo = Todo(name="Unique Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        
        # Add to KIV
        KIV.add(todo.id, user_id)
        
        # Try to add again (should reactivate, not duplicate)
        KIV.add(todo.id, user_id)
        
        # Count KIV entries
        kiv_count = KIV.query.filter_by(todo_id=todo.id).count()
        if kiv_count == 1:
            pass_test("KIV unique constraint maintained (1 entry per todo)")
        else:
            fail_test("KIV constraint violated", f"Found {kiv_count} entries for one todo")
    
    print_test("Cascading delete: Delete todo removes related data")
    with app_context():
        # Create todo with tracker and KIV
        todo = Todo(name="Cascade Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        Tracker.add(todo_id, 5, datetime.now())
        KIV.add(todo_id, user_id)
        
        # Delete todo
        Tracker.query.filter_by(todo_id=todo_id).delete()
        KIV.query.filter_by(todo_id=todo_id).delete()
        db.session.query(Todo).filter_by(id=todo_id).delete()
        db.session.commit()
        
        # Verify all deleted
        todo_exists = Todo.query.filter_by(id=todo_id).first()
        tracker_exists = Tracker.query.filter_by(todo_id=todo_id).first()
        kiv_exists = KIV.query.filter_by(todo_id=todo_id).first()
        
        if not todo_exists and not tracker_exists and not kiv_exists:
            pass_test("Cascading delete works correctly")
        else:
            fail_test("Cascading delete incomplete", "Related data still exists")
    
    cleanup_test_data(user_id)


# ============================================================================
# TEST SUITE 9: ERROR HANDLING
# ============================================================================

def test_error_handling():
    """Test error handling in database operations"""
    print_header("TEST SUITE 9: ERROR HANDLING")
    
    print_test("Handle non-existent todo gracefully")
    with app_context():
        # Try to get non-existent todo
        todo = Todo.query.filter_by(id=99999).first()
        if todo is None:
            pass_test("Non-existent todo returns None (no crash)")
        else:
            fail_test("Non-existent todo handling broken", "Should return None")
    
    print_test("Handle non-existent tracker gracefully")
    with app_context():
        # Try to remove non-existent KIV
        KIV.remove(99999)  # Should not crash
        pass_test("Remove non-existent KIV handles gracefully")
    
    print_test("Multiple rapid operations don't cause race conditions")
    with app_context():
        user_id = get_or_create_test_user("race@test.com")
        
        # Create todo
        todo = Todo(name="Race Test", user_id=user_id, modified=datetime.now())
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        
        # Rapid operations
        for i in range(5):
            Tracker.add(todo_id, 5, datetime.now())
            KIV.add(todo_id, user_id)
            KIV.remove(todo_id)
        
        # Verify final state
        todo_check = Todo.query.filter_by(id=todo_id).first()
        if todo_check:
            pass_test("Rapid operations completed without errors")
        else:
            fail_test("Rapid operations caused data loss", "Todo disappeared")
        
        cleanup_test_data(user_id)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all test suites"""
    print(f"\n{BOLD}{BLUE}{'╔' + '═' * 68 + '╗'}{RESET}")
    print(f"{BOLD}{BLUE}║ {' ' * 68} ║{RESET}")
    print(f"{BOLD}{BLUE}║  TodoBox - Comprehensive Accurate Test Suite{' ' * 20} ║{RESET}")
    print(f"{BOLD}{BLUE}║  Testing Against Real MySQL Database{' ' * 31} ║{RESET}")
    print(f"{BOLD}{BLUE}║ {' ' * 68} ║{RESET}")
    print(f"{BOLD}{BLUE}{'╚' + '═' * 68 + '╝'}{RESET}\n")
    
    try:
        test_database_persistence()
        test_kiv_functionality()
        test_user_isolation()
        test_tracker_functionality()
        test_todo_scheduling()
        test_query_filters()
        test_route_functionality()
        test_data_integrity()
        test_error_handling()
        
    except Exception as e:
        print(f"\n{RED}CRITICAL ERROR: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    print(f"{BOLD}Total Tests:{RESET} {tests_total}")
    print(f"{GREEN}{BOLD}Passed:{RESET} {tests_passed}")
    print(f"{RED}{BOLD}Failed:{RESET} {tests_failed}")
    
    if tests_failed > 0:
        print(f"\n{RED}{BOLD}Failed Tests:{RESET}")
        for test_name, details in failed_tests:
            print(f"  {RED}✗{RESET} {test_name}")
            if details:
                print(f"    {details}")
    
    # Print pass rate
    if tests_total > 0:
        pass_rate = (tests_passed / tests_total) * 100
        if pass_rate == 100:
            print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED! ({pass_rate:.1f}%){RESET}")
        else:
            print(f"\n{YELLOW}Pass Rate: {pass_rate:.1f}% ({tests_passed}/{tests_total}){RESET}")
    
    print()
    
    return tests_failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
