# Test Coverage Gap Analysis: KIV Visibility Bug

## Problem
The KIV (Keep In View) visibility bug was not caught by the comprehensive test suite. When marking a todo as KIV today, it would disappear from the uncompleted list but NOT appear in the KIV tab.

## Root Cause of Bug
In the `/undone` route (`app/routes.py`), the logic was checking if a todo was from today/tomorrow BEFORE checking if it was marked as KIV:

```python
# BUGGY CODE (before fix)
if todo_date == today or todo_date == tomorrow:
    continue  # Skip - but this includes KIV todos!

if KIV.is_kiv(todo.id):
    kiv_todos.append((todo, latest_tracker))
```

When marking a todo as KIV, the `todo.modified` field is updated to `datetime.now()`, giving it today's date. The buggy code would skip it before even checking the KIV status.

## Why Tests Didn't Catch This
### 1. Model-Level Tests Only
The existing KIV tests in `test_accurate_comprehensive.py` only test the KIV model methods:
```python
def test_kiv_functionality():
    """Test KIV table operations"""
    KIV.add(todo_id, user_id)
    KIV.is_kiv(todo_id)
    KIV.remove(todo_id)
```

These tests verify that data is correctly stored/retrieved from the KIV table, but they DON'T test the business logic of the `/undone` route.

### 2. Missing Route-Level Integration Tests
The route test (`test_route_functionality`) does NOT replicate the real scenario:
```python
# INCOMPLETE TEST LOGIC
if latest_tracker.status_id != 6 and not KIV.is_kiv(todo.id):
    undone.append(todo)
elif KIV.is_kiv(todo.id):
    kiv.append(todo)
```

This test logic:
- ✗ Does NOT include date filtering (today/tomorrow check)
- ✗ Does NOT create todos with old dates that need to be KIVed
- ✗ Does NOT verify that KIV todos are included despite date filtering

### 3. No End-to-End HTTP Tests
There are no tests that:
- Create a todo with an old date
- Mark it as KIV via HTTP POST
- Verify it appears in the `/undone?tab=kiv` response

## What Was Missing

### Gap 1: Date Filtering Logic Not Tested
The test suite didn't include the date filtering behavior that's central to the `/undone` route:
```python
# This logic was missing from tests:
today = date.today()
tomorrow = today + timedelta(days=1)
todo_date = todo.modified.date()
if todo_date == today or todo_date == tomorrow:
    continue  # Skip today/tomorrow - but this should not skip KIV!
```

### Gap 2: Temporal Scenario Not Tested
The bug only manifests when:
1. A todo has a modified date from the past (or any date except today/tomorrow)
2. That todo is marked as KIV (which updates modified to today)
3. We check if it appears in the KIV tab

The test suite never created todos with past dates and then marked them as KIV.

### Gap 3: Route Order-of-Operations Not Tested
The bug was about the ORDER of checks in the route:
1. Should check KIV status FIRST
2. Then check date filtering

The test suite didn't verify this order by testing with dates that would trigger the filtering logic.

## Solution: New Test Created
File: `tests/test_kiv_visibility_fix.py`

This test covers:
1. ✅ Create todo with old date (yesterday)
2. ✅ Verify it appears in uncompleted todos
3. ✅ Mark as KIV (which updates modified to today)
4. ✅ Verify it appears in KIV tab (not filtered out)
5. ✅ Verify it's no longer in uncompleted tab
6. ✅ Integration test via actual HTTP route

## Lessons Learned

### For Test Strategy
1. **Test Business Logic, Not Just Data**: Don't just test that CRUD operations work; test that the business rules (filtering, ordering, visibility) are correct
2. **Test Edge Cases with Temporal Aspects**: When dates are involved, test boundary conditions
3. **Test Route-Level Logic Completely**: Include all filtering/transformation steps in route tests
4. **End-to-End Integration Tests**: Complement unit tests with route-level HTTP tests

### For Code Review
1. **Date-Related Changes**: Any update to a `modified` or `target_date` field should trigger review of all query logic that uses those fields
2. **Conditional Logic Order**: When checking multiple conditions (is_kiv, status, date), document and test the order
3. **Negative Cases**: Test what happens when conditions interact (e.g., a KIV todo that's also from today)

### For Future Development
1. Add route-level tests that include all filtering logic
2. Create temporal test fixtures (todos from yesterday, today, tomorrow, future)
3. Test state transitions (e.g., marking KIV updates modified date; does it still filter correctly?)

## Running the New Test

```bash
# Run just the new KIV visibility tests
pytest tests/test_kiv_visibility_fix.py -v -s

# Run all KIV-related tests
pytest tests/test*kiv*.py -v

# Run comprehensive test suite
pytest tests/test_accurate_comprehensive.py -v
```

## Prevention Going Forward

1. **Pre-Commit Checklist**: When modifying filtering/sorting logic:
   - [ ] All conditions in filter/sort documented in comments
   - [ ] Order of conditions justified
   - [ ] Edge cases (empty lists, special statuses, etc.) tested
   - [ ] Integration tests written

2. **Test Coverage Goals**:
   - Unit tests: Model methods (currently passing ✓)
   - Integration tests: Route logic with edge cases (previously missing, now added)
   - End-to-end tests: HTTP requests with realistic scenarios (improved)

3. **Code Review Questions**:
   - "Does the test cover all branches of the filter logic?"
   - "Are there temporal edge cases being tested?"
   - "Does the test replicate the exact sequence of operations in the route?"
