# Service Worker External Resource Fix (CRITICAL)

## Issue
In production, clicking the "today" tab and loading the dashboard caused numerous console errors:

```
A ServiceWorker passed a promise to FetchEvent.respondWith() that resolved 
with non-Response value 'undefined'
```

Multiple external resources failed to load:
- `moment.js` from cdnjs.cloudflare.com
- `flatpickr` from cdn.jsdelivr.net
- Gravatar avatars from gravatar.com
- Google Fonts from fonts.googleapis.com
- Cloudflare Insights beacon
- Font Awesome CSS

Result: JavaScript error "Uncaught ReferenceError: flatpickr is not defined" prevented the today/list page from working.

## Root Cause
The service worker was intercepting ALL requests, including external third-party resources. When these external requests failed (network issues, CORS, etc.), the service worker's fetch handler would either:
1. Return `undefined` instead of a Response object
2. Try to cache resources it shouldn't cache

The browser's `respondWith()` method requires a Response object, not `undefined`, causing the error.

## Solution (FINAL)
The fix is simple and clean: **Don't intercept external resources at all.**

```javascript
// Skip external resources completely - let browser handle them
// This prevents service worker from interfering with CDN resources, gravatar, etc.
if (isExternalResource(url)) {
  // Don't intercept - let browser fetch normally
  return;
}
```

### Key Changes
1. **Added External Resource Detection** (lines 38-45):
   ```javascript
   function isExternalResource(url) {
     try {
       const urlObj = new URL(url);
       const currentOrigin = new URL(self.location).origin;
       return urlObj.origin !== currentOrigin;
     } catch (e) {
       return false;
     }
   }
   ```

2. **Skip Intercepting External Resources** (lines 73-77):
   - Returns early without calling `event.respondWith()`
   - Lets browser fetch external resources naturally
   - No service worker interference or caching

3. **Updated Cache Versions** (lines 2-3):
   - `CACHE_NAME`: v2 → v3
   - `STATIC_CACHE_NAME`: v2 → v3
   - Forces browsers to reload the new service worker

4. **Kept Safe Response Handling for Own Domain**:
   - Internal routes still use proper error handling
   - Always returns valid Response objects (never undefined)
   - Maintains caching strategy for /static/ assets

## Why This Works
- **External resources bypass service worker**: No interference with CDN requests
- **Browser handles failures naturally**: CORS errors, timeouts, etc. don't break SW
- **Fallback images work**: HTML `onerror` attribute on images still functions
- **No invalid Response objects**: Service worker never returns undefined
- **Cache version bump forces update**: Browsers reload SW with new logic

## Testing Verification
Users should:
1. ✅ Click "today" tab without console errors
2. ✅ Dashboard displays donut chart properly
3. ✅ Gravatar avatars load (or show fallback image)
4. ✅ No "non-Response value 'undefined'" errors
5. ✅ No "flatpickr is not defined" error

## Browser Update Instructions
For users seeing cached old service worker:

1. Open DevTools (F12)
2. Go to Application → Service Workers
3. Click "Unregister" for the old service worker
4. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
5. New v3 service worker will install automatically

## Files Modified
- `app/static/service-worker.js` - Core fix
  - Added `isExternalResource()` function
  - Modified fetch handler to skip external resources
  - Updated cache versions to force reload
- `CHANGELOG.md` - Documented the fix

## Best Practice Insight
**Service workers should only intercept requests they can handle properly.**

When a service worker can't provide a valid response (no cache, no network), it must either:
- Return a valid Response object (even if error status)
- NOT call `event.respondWith()` at all (let browser handle it)

Never return `undefined` - the browser has no fallback for that.

