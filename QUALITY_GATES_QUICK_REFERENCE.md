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

⚠️ **Important**: Pre-push hook **only works for local terminal `git push`**. For GitHub web push, use Branch Protection Rules (see below).

**That's it!** The system does the rest.

---

## 🔐 GitHub Web Push Protection

**Problem**: Pre-push hooks don't run when pushing via GitHub web interface.

**Solution**: Enable **GitHub Branch Protection Rules** to protect master from all push methods:

1. Go to: GitHub → Repository Settings → Branches
2. Click "Add rule" 
3. Enter: `master`
4. Enable:
   - ✓ Require a pull request before merging
   - ✓ Require approvals (suggest 1+)
   - ✓ Dismiss stale pull request approvals
   - ⊙ Require status checks to pass: **SKIP THIS** (requires GitHub Actions)

**Result**: Master is protected from direct pushes (web UI + local). Code requires review.

---

## What Happens Automatically

### At Commit Time (Local - All Users)
- ✓ Python syntax validation
- ✓ Import resolution check
- ✓ requirements.txt validation
- ✓ Unit tests (9 critical tests)
- ✓ API route tests (2 critical tests)
- ✓ Critical file dependency checks

### At Push to Master (Local Terminal Only)
- ✓ Full test suite (all 41 tests)
- ✓ Requirements conflict detection
- ✓ Import validation
- ✓ Critical API routes test
- ✓ Database integrity check
- ✓ Coverage metrics

### At GitHub Web Push (If Branch Protection Enabled)
- ✓ Requires pull request
- ✓ Requires code review approval
- ✓ Blocks direct master push from web UI
- ℹ️ Status checks optional (requires GitHub Actions setup)

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

## If Pre-Push Blocks You (Local Terminal)

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

## If GitHub Web Push is Blocked

**This means Branch Protection Rules are working!**

To push your changes:
1. Create a **pull request** (PR) instead of direct push
2. Ask a team member to review your PR
3. Merge via GitHub after approval
4. Branch protection ensures code quality even via web UI

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
