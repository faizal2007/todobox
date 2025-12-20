# Security Issue #85: Hardcoded Credentials Fix

## 🔴 CRITICAL Issue Found & Fixed

### Problem Identified
- Hardcoded database password in `.flaskenv` 
- Hardcoded Google OAuth credentials exposed
- Hardcoded local development IP in OAUTH_REDIRECT_URI

### Impact
These credentials are stored in git history and could allow unauthorized access to:
- Production database
- Google OAuth application
- User data and todos

### Solution Applied

#### 1. Cleared `.flaskenv` of all sensitive data
```env
✅ DB_PASSWORD removed
✅ DB_URL removed  
✅ DB_USER removed
✅ DB_NAME removed
✅ GOOGLE_CLIENT_ID removed
✅ GOOGLE_CLIENT_SECRET removed
✅ OAUTH_REDIRECT_URI removed
```

#### 2. Verified `.gitignore` protects `.flaskenv`
- `.gitignore` already contains `.flaskenv` rule
- Only `.flaskenv.example` is tracked (no secrets)

#### 3. Proper setup process documented
- Users should copy `.flaskenv.example` to `.flaskenv`
- Fill in credentials locally (never commit)
- Use environment variables in production

### 🚨 URGENT ACTION REQUIRED

If these credentials are used anywhere:

1. **Rotate Database Password**
   ```bash
   # In MySQL
   ALTER USER 'freakie'@'192.168.1.112' IDENTIFIED BY 'new-secure-password';
   FLUSH PRIVILEGES;
   ```

2. **Regenerate Google OAuth Credentials**
   - Visit: https://console.cloud.google.com/
   - Delete old credentials
   - Create new OAuth 2.0 Client ID
   - Update locally in `.flaskenv` (never commit)

3. **Rewrite Git History (if needed)**
   ```bash
   # WARNING: Only do this if you haven't shared the repo publicly
   # This permanently removes the secrets from git history
   git filter-branch --env-filter '
   if [ "$GIT_COMMIT" = <commit-hash> ]; then
     unset DB_PASSWORD
     unset GOOGLE_CLIENT_SECRET
   fi
   ' HEAD
   ```

### Setup Instructions for New Developers

1. Clone the repository
   ```bash
   git clone https://github.com/faizal2007/todobox.git
   cd todobox
   ```

2. Copy the example environment file
   ```bash
   cp .flaskenv.example .flaskenv
   ```

3. Edit `.flaskenv` and add your credentials
   ```bash
   vim .flaskenv
   ```

4. DO NOT commit `.flaskenv`
   ```bash
   # Verify .gitignore includes .flaskenv
   grep ".flaskenv" .gitignore
   ```

### Best Practices Implemented

✅ `.flaskenv` is in `.gitignore`
✅ `.flaskenv.example` is a template without secrets
✅ Clear documentation for credential management
✅ Environment-based configuration
✅ No hardcoded secrets in code

### Environment Variable Usage

Production deployments should use:
- Container secrets management (Docker/Kubernetes)
- Cloud provider secret managers (AWS Secrets Manager, Azure Key Vault, etc.)
- Environment variables set at deployment time
- Never store secrets in version control

### Verification

To verify no secrets remain in the repository:

```bash
# Search for common credential patterns
grep -r "password\s*=" .flaskenv .flaskenv.example | grep -v "^\s*#"
grep -r "secret\s*=" .flaskenv .flaskenv.example | grep -v "^\s*#"

# Both should show only examples/comments, never actual values
```

---

## Files Modified

- ✅ `.flaskenv` - Cleared of all credentials
- ✅ `.flaskenv.example` - Verified as template only
- ✅ `.gitignore` - Verified `.flaskenv` is ignored

## Status

🟢 **FIXED** - All hardcoded credentials removed
🟢 **SECURED** - `.gitignore` properly configured
🟢 **DOCUMENTED** - Setup guide provided

## Related Issues
- GitHub Security Alert: Hardcoded credentials
- GitHub Code Scanning Issue #85
