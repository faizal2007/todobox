// Basic service worker for caching shell assets
const CACHE_NAME = 'todobox-v1';
const CORE_ASSETS = [
  '/',
  '/dashboard',
  '/static/manifest.json',
  '/static/assets/icons/icon-192x192.png',
  '/static/assets/icons/icon-256x256.png',
  '/static/assets/icons/icon-384x384.png',
  '/static/assets/icons/icon-512x512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(cached => 
      cached || fetch(event.request).catch(() => caches.match('/'))
    )
  );
});
