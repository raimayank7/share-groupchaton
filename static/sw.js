/* Share by GroupChatOn — service worker.
   Bump VERSION whenever cached files change so old caches are dropped. */
const VERSION = 'share-v1';
const STATIC_CACHE = VERSION + '-static';
const PAGE_CACHE = VERSION + '-pages';
const PRECACHE = ['/', '/search/'];

// Never touch ads, analytics or the Apps Script backend.
const BYPASS = /(googlesyndication|google-analytics|googletagmanager|doubleclick|script\.google\.com|script\.googleusercontent\.com)/;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(PAGE_CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      .catch(() => {})
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => !k.startsWith(VERSION + '-')).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function cacheFirst(request) {
  return caches.match(request).then((hit) => hit || fetch(request).then((res) => {
    if (res && res.ok) {
      const copy = res.clone();
      caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy));
    }
    return res;
  }));
}

function networkFirst(request, isPage) {
  return fetch(request).then((res) => {
    if (res && res.ok) {
      const copy = res.clone();
      caches.open(PAGE_CACHE).then((cache) => cache.put(request, copy));
    }
    return res;
  }).catch(() => caches.match(request, { ignoreSearch: isPage }).then((hit) => {
    if (hit) return hit;
    if (isPage) return caches.match('/');
    return Response.error();
  }));
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (BYPASS.test(url.hostname)) return;
  if (url.origin !== self.location.origin) return;

  const path = url.pathname;
  if (path.startsWith('/assets/') || path.startsWith('/brand/') || path.startsWith('/media/')) {
    event.respondWith(cacheFirst(request));
    return;
  }
  const isPage = request.mode === 'navigate' || (request.headers.get('accept') || '').includes('text/html');
  if (isPage || path === '/data/index.json') {
    event.respondWith(networkFirst(request, isPage));
  }
});
