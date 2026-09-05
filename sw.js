const CACHE_NAME = 'yang-pwa-v68';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  './photos/raccoon_pet.png',
  './photos/raccoon_avatar.png',
  './photos/avatar_yang.png',
  './photos/basashi.jpg',
  './photos/akaushi.jpg',
  './apple-touch-icon-precomposed.png',
  './icons/tanuki.png',
  './icons/apple-touch-icon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// 網路優先 (Network-First) 策略：優先獲取最新程式碼，斷網時無縫切換快取
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          if (event.request.destination === 'document') {
            return caches.match('./index.html');
          }
        });
      })
  );
});
