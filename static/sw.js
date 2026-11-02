/* Share by GroupChatOn — service worker.
   Bump VERSION whenever cached files change so old caches are dropped. */
const VERSION = 'share-v2';
const STATIC_CACHE = VERSION + '-static';
const PAGE_CACHE = VERSION + '-pages';
const PRECACHE = ['/', '/search/'];
// Sponsor cards work offline too: the sponsor list (/promos.json) and every sponsor picture (on Blogger's image server)
// are kept in their own cache, refreshed whenever the list is fetched online; sponsors that were removed are dropped.
const SPONSOR = 'share-sponsor';
const SPONSOR_IMG = /^(blogger\.googleusercontent\.com|[\w-]+\.bp\.blogspot\.com)$/;

function saveSponsors(res) {
  return caches.open(SPONSOR).then((cache) => {
    const got = res ? Promise.resolve(res) : fetch('/promos.json', { cache: 'no-cache' });
    return got.then((r) => {
      if (!r || !r.ok) return;
      return cache.put('/promos.json', r.clone()).then(() => r.json()).then((P) => {
        const imgs = [];
        ((P && P.promos) || []).forEach((p) => (p.imgs || []).forEach((u) => imgs.push(u)));
        return cache.keys().then((keys) => Promise.all([
          ...keys.filter((k) => /^https?:/.test(k.url) && !k.url.endsWith('/promos.json') && imgs.indexOf(k.url) < 0).map((k) => cache.delete(k)),
          ...imgs.map((u) => cache.match(u).then((hit) => hit || fetch(new Request(u, { mode: 'no-cors' })).then((ir) => cache.put(u, ir))).catch(() => {}))
        ]));
      });
    }).catch(() => {});
  });
}

// Never touch ads, analytics or the Apps Script backend.
const BYPASS = /(googlesyndication|google-analytics|googletagmanager|doubleclick|script\.google\.com|script\.googleusercontent\.com)/;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(PAGE_CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      .catch(() => {})
      .then(() => { saveSponsors(); return self.skipWaiting(); })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => !k.startsWith(VERSION + '-') && k !== SPONSOR).map((k) => caches.delete(k))))
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
  if (SPONSOR_IMG.test(url.hostname) && request.destination === 'image') {   // a sponsor picture: saved copy first
    event.respondWith(caches.open(SPONSOR).then((cache) => cache.match(request.url).then((hit) => hit || fetch(request).then((res) => {
      if (res && (res.ok || res.type === 'opaque')) cache.put(request.url, res.clone());
      return res;
    }))));
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (url.pathname === '/promos.json') {   // the sponsor list: fresh when online (and its pictures saved), saved copy offline
    event.respondWith(fetch(request, { cache: 'no-cache' }).then((res) => {
      if (res && res.ok) saveSponsors(res.clone());
      return res;
    }).catch(() => caches.open(SPONSOR).then((cache) => cache.match('/promos.json')).then((hit) => hit || Response.error())));
    return;
  }

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
