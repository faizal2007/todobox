# 🚀 Quality Gate Setup Guide

This guide will set up the comprehensive testing and quality gate system that prevents production breaks.

## ⚡ Quick Setup (2 minutes)

```bash
# Install pre-commit hook
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Install pre-push hook  
cp .git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Make scripts executable
chmod +x scripts/validate_requirements.py
chmod +x scripts/run_comprehensive_tests.py

# Test the setup
python scripts/validate_requirements.py
```

---

## 🧪 What You Now Have

### Pre-Commit Protection
- Runs automatically when you `git commit`
- Blocks commits if:
  - Python syntax is invalid
  - Imports fail
  - requirements.txt has conflicts
  - Tests fail
  - Critical files changed without testing

### Pre-Push Protection (Master Only)
- Runs automatically when you `git push origin master`
- Blocks push if:
  - Full test suite (all 41 tests) fails
  - Requirements validation fails
  - Any critical test fails

### Validation Scripts
- `scripts/validate_requirements.py` - Dependency validation
- `scripts/run_comprehensive_tests.py` - Full test suite

---

## 📊 Typical Workflow

### Make and Commit Changes
```bash
# 1. Edit files
nano app/routes.py

# 2. Stage changes
git add app/routes.py

# 3. Commit (pre-commit checks run)
git commit -m "FIX: Update todo endpoint"

# Output:
# 🔍 Running pre-commit checks...
#   • Checking Python syntax... ✓
#   • Checking imports... ✓
#   • Validating requirements.txt... ✓
#   • Running quick unit tests... ✓
#   • Running API route tests... ✓
# ✅ All pre-commit checks passed - commit allowed
```

### Push to Master
```bash
# 4. Push to master (pre-push checks run)
git push origin master

# Output:
# 🚀 PRE-PUSH VERIFICATION CHECKS
# ⚠️  MASTER BRANCH DETECTED - Running comprehensive checks...
#
#   1️⃣  Running FULL test suite (all 41 tests)... ✓
#   2️⃣  Validating requirements.txt dependencies... ✓
#   3️⃣  Checking all imports... ✓
#   4️⃣  Testing critical API routes... ✓
#   5️⃣  Checking database integrity... ✓
#
# ✅ All pre-push checks passed - push allowed
```

---

## 🔧 Troubleshooting

### Pre-commit hook not running?
```bash
# Check if installed
ls -la .git/hooks/pre-commit

# If not there, install it
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Pre-push hook not running?
```bash
# Check if installed
ls -la .git/hooks/pre-push

# If not there, install it
cp .git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

### Getting "Permission denied" on hooks?
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### Commit blocked - what to do?
```bash
# 1. Read the error message
# 2. Run the suggested command to debug
# 3. Fix the issue
# 4. Try committing again

# Example: If tests fail
pytest tests/ -v --tb=short

# Fix the failing tests
# Then commit again
git add .
git commit -m "FIX: Resolve test failures"
```

### Push blocked to master - what to do?
```bash
# 1. The pre-push hook already told you what failed
# 2. Run the full test suite locally
pytest tests/ -v

# 3. Fix any issues
# 4. Commit the fixes
# 5. Try pushing again
git push origin master
```

### Emergency override (NOT RECOMMENDED)
```bash
# Skip all pre-commit checks
git commit --no-verify

# Skip all pre-push checks  
git push --no-verify

# ⚠️  ONLY use in genuine emergencies!
# After using --no-verify:
# 1. Run full tests immediately
# 2. Notify team immediately
# 3. Be prepared to rollback
```

---

## 📋 Checklist

- [ ] Pre-commit hook installed (`ls -la .git/hooks/pre-commit`)
- [ ] Pre-push hook installed (`ls -la .git/hooks/pre-push`)
- [ ] Scripts are executable (`chmod +x scripts/*.py`)
- [ ] Hooks are executable (`chmod +x .git/hooks/pre-*`)
- [ ] Tested pre-commit: `git add file && git commit`
- [ ] No errors during pre-commit check
- [ ] Tested validation: `python scripts/validate_requirements.py`
- [ ] Ready to use

---

## 🎯 Key Differences From Old Setup

| Aspect | Old | New |
|--------|-----|-----|
| Requirements validation | Caught in production | Caught at commit time |
| Syntax errors | Committed, caught in tests | Blocked at commit |
| Incomplete functions | Committed, broke production | Blocked at commit |
| API route breakage | Tests passed, broke in prod | Full tests run at push time |
| Pre-push to master | No checks | Full suite (41 tests) runs |

---

## 📞 Need Help?

1. **Hook won't run?**
   - Check permissions: `ls -la .git/hooks/`
   - Reinstall: `cp .git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`

2. **Tests failing?**
   - Run locally first: `pytest tests/ -v`
   - See detailed output: `pytest tests/ -v --tb=short`
   - Run specific test: `pytest tests/test_all_routes.py::TestAPIRoutes::test_update_todo_api -xvs`

3. **Requirements validation failing?**
   - Check specific issues: `python scripts/validate_requirements.py`
   - Review the output carefully
   - Fix conflicts in requirements.txt

4. **Need to understand what's being checked?**
   - See: `docs/TESTING_AND_QUALITY_GATES.md`
   - Review: `.git-hooks/pre-commit` (what runs before commit)
   - Review: `.git-hooks/pre-push` (what runs before push to master)

---

## ✨ You're Protected

After setup, you have:
- ✅ No broken code gets committed
- ✅ No dependency conflicts reach production
- ✅ No incomplete functions survive
- ✅ No untested changes to master
- ✅ Full confidence in deployment

**That's the goal: Production never breaks again.**
