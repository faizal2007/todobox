# Donut Chart Service Worker Fix

## Issue
In production, the donut chart was not displaying and the browser console showed this error:

```
Failed to load 'https://www.gravatar.com/avatar/e4f36b24bbefaf33264699d4be5e1d0a?s=32&d=identicon'. 
A ServiceWorker passed a promise to FetchEvent.respondWith() that resolved with 
non-Response value 'undefined'. service-worker.js:73:11
```

## Root Cause
The service worker's fetch event handler had a flaw in error handling:

```javascript
.catch(() => {
  // Return cached version only if network fails
  return caches.match(request).then(cached => cached);
  // ^ This returns 'undefined' if no cached version exists!
})
```

When a fetch request failed (e.g., Gravatar temporarily unavailable) and there was no cached version, the promise resolved with `undefined`. The ServiceWorker's `respondWith()` method requires a Response object, not `undefined`.

## Solution
The fix includes three key improvements:

### 1. Added External Resource Detection
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

This function detects third-party domains (gravatar.com, CDNs, etc.) and handles them differently.

### 2. Special Handling for External Resources
External resources are now handled with network-first strategy without caching:

```javascript
if (isExternalResource(url)) {
  event.respondWith(
    fetch(request).catch(() => {
      // Return empty 503 response instead of undefined
      return new Response('', { status: 503, statusText: 'Service Unavailable' });
    })
  );
  return;
}
```

This prevents external resource failures from blocking the service worker.

### 3. Proper Error Responses
All error cases now return valid Response objects:

```javascript
.catch(() => {
  return caches.match(request).then(cached => {
    if (cached) {
      return cached;
    }
    // Return a proper Response object instead of undefined
    return new Response(
      JSON.stringify({ error: 'Service unavailable' }),
      { status: 503, statusText: 'Service Unavailable', headers: { 'Content-Type': 'application/json' } }
    );
  });
})
```

## Impact
- ✅ Dashboard donut charts now display without errors
- ✅ Gravatar avatars load without blocking the service worker
- ✅ Service worker gracefully handles unavailable external resources
- ✅ No more "non-Response value 'undefined'" errors in console
- ✅ Better user experience when third-party services are temporarily unavailable

## Files Modified
- `app/static/service-worker.js` - Added external resource detection and proper error handling

## Testing
To verify the fix works:

1. Open the dashboard (where the donut chart is displayed)
2. Check browser DevTools Console - should see no service worker errors
3. Temporarily disable network access to gravatar.com - avatar should fail gracefully
4. Donut chart should continue to display normally

## Related Files
- `app/templates/dashboard.html` - Contains the donut chart implementation and Chart.js configuration
- `app/routes.py` - `/dashboard` route that provides `time_period_data` and `chart_segments`
