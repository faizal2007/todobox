---
For: PWA Installation Button Troubleshooting
Read Time: 8 min
Status: Ready for Use
Last Updated: 2025-12-03
Related Documentation:
  - PWA_MANIFEST_DYNAMIC.md
  - Architecture: docs/ARCHITECTURE.md
---

# PWA Install Button Troubleshooting Guide

## Overview

The app now includes diagnostic tools to help identify why the "Install App" button might not be appearing on mobile. This document explains how to use these tools and interpret the results.

## Quick Start: Using the PWA Debug Button

### For Users:
1. Open the app on your mobile device in a web browser
2. Look for the **"PWA Debug"** button in the top-right corner (next to notifications)
3. Click it to see diagnostic information
4. An alert will show you the PWA status

### For Developers:
1. Open the browser's **Developer Console** (Press F12 or Cmd+Option+J)
2. Look at the console output - it will show:
   - ✓ Service Worker registered
   - ✓ beforeinstallprompt event fired (if it happened)
   - ⚠️ Warnings if something is missing

## How the PWA Install Button Works

### The Process:
1. **Page Loads** → JavaScript initializes
2. **Service Worker Registers** → Makes the app "installable"
3. **beforeinstallprompt Event Fires** → Browser detects PWA is ready
4. **Install Button Appears** → User can click to install

### Why It Might NOT Work:

| Issue | Cause | Solution |
|-------|-------|----------|
| Button never appears | `beforeinstallprompt` event didn't fire | See below ↓ |
| App already installed | Browser thinks app is already installed | Uninstall app, clear cache, refresh |
| Using HTTP (not HTTPS) | PWA requires secure connection | Use HTTPS URL |
| Browser doesn't support | Older browsers, or Safari on iOS | Different install method per browser |
| Service Worker failed | Installation file corrupted or inaccessible | Check `/static/service-worker.js` |
| Manifest invalid | JSON syntax error or missing fields | Click PWA Debug to test |
| App criteria not met | Missing icons, no scope, display mode wrong | Check manifest endpoint |

## Step-by-Step Diagnostic Process

### Step 1: Open Developer Console

**Chrome/Android:**
```
1. Tap three dots (menu) → Settings → Developer menu
2. Tap "Developer menu" (might need to tap Build Number 7 times first)
3. Enable USB debugging → Connect to computer
4. Use Chrome Remote Debugger: chrome://inspect
```

**Safari/iOS:**
```
1. On Mac: Safari → Develop → [your device] → [app URL]
2. You'll see console output
3. iOS doesn't show console on device directly
```

### Step 2: Run the PWA Debug Button

Click the **"PWA Debug"** button (gray bug icon) in the top-right.

You'll see a popup with information like:

```
beforeinstallprompt received: NO
Button visible: NO
Service Worker support: YES
getInstalledRelatedApps support: YES
Manifest URL: /manifest.json
User Agent: Mozilla/5.0 (Linux; Android 13) ...
Current URL: https://example.com/dashboard
HTTPS: YES
Standalone mode: Not supported
Manifest valid: ✓ Yes
Manifest name: Shimasu - Todo Task Manager
```

### Step 3: Interpret the Results

#### ✓ Everything is YES/Working:
```
beforeinstallprompt received: YES → Install button should be visible
Manifest valid: YES
Service Worker support: YES
HTTPS: YES
```
**Action:** Refresh page. If button still not visible, it was already installed (uninstall first).

#### ✗ beforeinstallprompt received: NO
```
Possible reasons:
1. App is already installed (uninstall first)
2. Browser does not support install prompts
3. Not accessed via HTTPS (required for PWA)
4. Service Worker registration failed
5. User previously dismissed the install prompt
6. PWA criteria not met (icons, manifest, etc.)
```

**Actions to try:**
1. **Check HTTPS** - If "HTTPS: NO", you need to use HTTPS URL
2. **Check Manifest Valid** - If "Manifest valid: NO", there's a problem with `/manifest.json` endpoint
3. **Check Service Worker** - If "Service Worker support: NO", browser is too old
4. **Uninstall App** - If you installed it before, uninstall and try again
5. **Clear Cache** - Browser cache might block re-prompting

### Step 4: Console Logging

Open browser console (F12) and look for these messages:

**Success (you should see this):**
```
✓ Service Worker registered: { scope: '/', ... }
✓ beforeinstallprompt event fired - APP IS INSTALLABLE
✓ Install button now VISIBLE
```

**Failure (this needs fixing):**
```
✗ Service Worker failed: {error message}
⚠️ beforeinstallprompt did NOT fire within 5 seconds
⚠️ Install button element not found
```

## Browser-Specific Install Methods

### Chrome (Android) - Supports beforeinstallprompt ✓
```
1. Open app in Chrome
2. "Install App" button should appear
3. Click it → Select "Install"
4. App added to home screen
```

**If not working:**
- Check HTTPS connection
- Clear browser cache
- Try incognito mode
- Uninstall previous version if exists

### Safari (iOS) - Does NOT support beforeinstallprompt ✗
```
1. Open app in Safari
2. Tap Share button (bottom or top)
3. Scroll down → "Add to Home Screen"
4. Tap it → Name → Add
```

**Our workaround:**
- App shows helpful message when Safari detected
- Meta tags enable: `apple-mobile-web-app-capable: yes`
- Status bar color applies automatically
- Full-screen display works like native app

### Firefox (Android) - Limited Support
```
1. Open app in Firefox
2. May not show install button
3. Manual install not well-supported
4. Recommend Chrome instead
```

### Samsung Internet (Android) - Supports beforeinstallprompt ✓
```
Similar to Chrome, should work fine
```

## Testing Locally

### Setup HTTPS Locally (Required for PWA):
```bash
# 1. Generate self-signed certificate (one time)
mkdir -p ~/.ssl
openssl req -x509 -newkey rsa:2048 -keyout ~/.ssl/key.pem \
  -out ~/.ssl/cert.pem -days 365 -nodes

# 2. Run app with HTTPS
gunicorn --certfile=~/.ssl/cert.pem \
  --keyfile=~/.ssl/key.pem \
  --bind 0.0.0.0:443 \
  "app:app"

# 3. Access via https://localhost:443
# Accept the security warning in browser
```

### Without HTTPS:
```bash
# beforeinstallprompt won't fire (PWA requires HTTPS)
# But you can test the manifest and service worker:

# Check manifest
curl https://your-domain.com/manifest.json

# Check service worker
curl https://your-domain.com/service-worker.js

# Check pages load with PWA meta tags
curl https://your-domain.com/dashboard | grep "manifest\|mobile-web-app"
```

## Common Issues and Fixes

### Issue: Manifest endpoint returns 404

**Problem:** `/manifest.json` endpoint not working

**Fix:**
```python
# Check app/routes.py has this endpoint:
@app.route('/manifest.json')
def get_manifest():
    manifest = {
        "name": f"{config.TITLE} - Todo Task Manager",
        ...
    }
    return jsonify(manifest)
```

**Test:**
```bash
curl https://your-domain.com/manifest.json
```

### Issue: Service Worker registration fails

**Problem:** Error in console: `Service Worker registration failed`

**Fix:**
1. Check `/static/service-worker.js` exists and is readable
2. Verify no JavaScript errors in service-worker.js
3. Clear browser cache and service workers:
   - Chrome DevTools → Application → Service Workers → Unregister all
   - Refresh page

**Test:**
```bash
# Check file exists
ls -la app/static/service-worker.js

# Check file is accessible
curl https://your-domain.com/static/service-worker.js | head -20
```

### Issue: Button visible but install fails

**Problem:** Button appears, but clicking it shows error

**Fix:**
1. Manifest might be invalid JSON
2. Click PWA Debug button to test manifest validity
3. If manifest.json returns error, check app/routes.py for bugs

**Test:**
```bash
# Validate manifest JSON
curl https://your-domain.com/manifest.json | python -m json.tool
```

### Issue: App already installed warning

**Problem:** Button doesn't appear because app thinks it's already installed

**Fix:**
1. On device: Go to Settings → Apps → Uninstall "[TITLE] TodoBox"
2. Or if it's a shortcut: Delete from home screen
3. Close all browser tabs with the app
4. Refresh the app page
5. Button should now appear

## Debugging Commands

### Monitor Console in Real-Time:
```bash
# Use ngrok to expose local HTTPS
ngrok http https://localhost:443
# Then access via ngrok URL from phone
# Console logs appear in terminal
```

### Test Manifest Programmatically:
```python
import requests

resp = requests.get('https://your-domain.com/manifest.json')
print('Status:', resp.status_code)
print('Manifest:', resp.json())

# Check required fields
manifest = resp.json()
required = ['name', 'short_name', 'icons', 'start_url', 'display', 'scope']
for field in required:
    print(f"✓ {field}: {field in manifest}")
```

### Test Service Worker:
```bash
# Check if it responds
curl -I https://your-domain.com/service-worker.js

# Should return 200 with Content-Type: application/javascript
```

### Clear PWA Installation (Developers):
```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then(regs => {
    regs.forEach(reg => reg.unregister());
    console.log('All Service Workers unregistered');
    location.reload();
});
```

## Code Changes Made

### Added in this session:
1. **PWA Debug Button** - Visual diagnostic tool for users
2. **Enhanced Console Logging** - Detailed output for developers
3. **5-Second Timeout** - Detects when beforeinstallprompt doesn't fire
4. **Manifest Validation** - Tests if manifest.json is accessible
5. **Browser Detection** - Helps identify compatibility issues

### Files Modified:
- `app/templates/main.html` - Added PWA debug tools
- `app/routes.py` - Dynamic manifest endpoint (✓ existing)
- `app/static/css/style.css` - Button styling (✓ existing)
- `app/static/service-worker.js` - Service worker (✓ existing)

## Next Steps if Still Not Working

1. **Check HTTPS:** PWA absolutely requires HTTPS (except localhost)
2. **Uninstall App:** Remove from device if installed before
3. **Clear Browser Cache:** Settings → Clear cache/cookies
4. **Test in Incognito/Private:** Fresh browser state
5. **Try Different Browser:** Chrome usually works best
6. **Share Console Logs:** Copy console.log output for debugging
7. **Check User Agent:** Some very old browsers not supported

## Resources

- [MDN: Web app manifests](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [MDN: beforeinstallprompt](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeinstallprompt_event)
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Workers Guide](https://developers.google.com/web/tools/chrome-devtools/service-workers)

---

**Last Tested:** 2025-12-03  
**Status:** All PWA endpoints verified working  
**Next Review:** When user reports button still not visible
