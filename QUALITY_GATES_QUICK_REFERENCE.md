# 🚨 Quality Gate Quick Reference

## For Developers: Daily Workflow

### Make Changes & Commit
```bash
git add file.py
git commit -m "FIX: description"
```
✅ Pre-commit checks run automatically  
✅ Blocked if syntax/imports/tests fail  
❌ Can't commit broken code

### Push to Master
```bash
git push origin master
```
✅ Pre-push checks run automatically  
✅ Blocks if tests fail  
✅ Blocks if requirements are invalid  
❌ Can't push broken code

**That's it!** The system does the rest.

---

## What Happens Automatically

### At Commit Time
- ✓ Python syntax validation
- ✓ Import resolution check
- ✓ requirements.txt validation
- ✓ Unit tests (9 critical tests)
- ✓ API route tests (2 critical tests)
- ✓ Critical file dependency checks

### At Push to Master
- ✓ Full test suite (all 41 tests)
- ✓ Requirements conflict detection
- ✓ Import validation
- ✓ Critical API routes test
- ✓ Database integrity check
- ✓ Coverage metrics

---

## If Pre-Commit Blocks You

```bash
# 1. Read the error message
# 2. Run the suggested diagnostic
# 3. Fix the issue

# Example: If tests fail
pytest tests/ -v --tb=short

# 4. Try commit again
git commit -m "message"
```

---

## If Pre-Push Blocks You

```bash
# 1. You were about to push to MASTER
# 2. Pre-push ran the full test suite
# 3. Something failed

# Run tests locally to see details
pytest tests/ -v

# Fix the issue
# Commit fix
git add .
git commit -m "FIX: whatever"

# Try push again
git push origin master
```

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `SyntaxError` | Check your Python code syntax |
| `ImportError` | Ensure all imports work with `python -c "from app import *"` |
| `Test failed` | Run `pytest tests/ -v` locally |
| `requirements.txt error` | Run `python scripts/validate_requirements.py` |
| `Hook not running` | Reinstall: `cp .git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` |

---

## Emergency Override (NOT RECOMMENDED)

```bash
# Only if truly necessary
git commit --no-verify  # Skip pre-commit
git push --no-verify    # Skip pre-push

# After using --no-verify:
# 1. Run tests immediately: pytest tests/ -v
# 2. Notify team
# 3. Monitor production closely
```

---

## Key Protections

### Before Commit
❌ Can't commit broken Python syntax  
❌ Can't commit unresolvable imports  
❌ Can't commit with failing tests  
❌ Can't commit with dependency conflicts  

### Before Push to Master
❌ Can't push without passing full test suite  
❌ Can't push with invalid requirements  
❌ Can't push with broken imports  
❌ Can't push without critical API tests passing  

---

## Status: Production Safe ✅

With this system:
- No broken code reaches production
- No dependency conflicts break deployments
- No incomplete functions survive
- No untested changes go to master
- Full confidence in every push

**Your production is protected.**
