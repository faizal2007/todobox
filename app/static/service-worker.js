// Service worker with proper cache strategy for authentication and dynamic content
const CACHE_NAME = 'todobox-v2';
const STATIC_CACHE_NAME = 'todobox-static-v2';

// Only cache static assets (CSS, JS, images, fonts, icons)
const STATIC_ASSETS = [
  '/static/manifest.json',
  '/static/assets/icons/icon-192x192.png',
  '/static/assets/icons/icon-256x256.png',
  '/static/assets/icons/icon-384x384.png',
  '/static/assets/icons/icon-512x512.png'
];

// Routes that should NEVER be cached (auth, sessions, API)
const NO_CACHE_ROUTES = [
  '/login',
  '/logout',
  '/auth/',
  '/api/',
  '/account',
  '/settings',
  '/sharing',
  '/dashboard',
  '/index'
];

// Check if URL should be cached
function shouldCache(url) {
  // Don't cache if it's a no-cache route
  if (NO_CACHE_ROUTES.some(route => url.includes(route))) {
    return false;
  }
  // Only cache static assets on our own domain
  if (url.includes('/static/')) {
    return true;
  }
  return false;
}

// Check if URL is external (third-party domain)
function isExternalResource(url) {
  try {
    const urlObj = new URL(url);
    const currentOrigin = new URL(self.location).origin;
    return urlObj.origin !== currentOrigin;
  } catch (e) {
    return false;
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== STATIC_CACHE_NAME && k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const { url, method } = request;

  // Only cache GET requests
  if (method !== 'GET') {
    return;
  }

  // For external resources (gravatar, CDNs, etc), use network-first without caching
  if (isExternalResource(url)) {
    event.respondWith(
      fetch(request).catch(() => {
        // For external resources, just let the browser handle the error
        // Don't return anything - this lets the browser's default behavior take over
        return new Response('', { status: 503, statusText: 'Service Unavailable' });
      })
    );
    return;
  }

  // Network-first for auth and dynamic content, cache-first for static assets
  if (shouldCache(url)) {
    // Cache-first strategy for static assets
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request))
    );
  } else {
    // Network-first strategy for everything else (auth, dynamic content, API)
    event.respondWith(
      fetch(request)
        .then(response => {
          // Clone response to cache it if needed
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return cached version only if network fails
          return caches.match(request).then(cached => {
            // Return cached response, or a proper error response if no cache
            if (cached) {
              return cached;
            }
            // Return a 503 Service Unavailable response instead of undefined
            return new Response(
              JSON.stringify({ error: 'Service unavailable' }),
              { status: 503, statusText: 'Service Unavailable', headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
  }
});

