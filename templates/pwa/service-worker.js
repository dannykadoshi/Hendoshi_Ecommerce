{% load static %}
const CACHE_VERSION = 'hendoshi-v1';
const STATIC_CACHE = 'hendoshi-static-v1';

// Core assets to pre-cache on install
const PRECACHE_URLS = [
    '/offline/',
    '{% static "images/icons/icon-192.png" %}',
    '{% static "images/icons/icon-512.png" %}',
    '{% static "images/pug-skull.webp" %}',
    '{% static "css/1-foundation/variables.css" %}',
    '{% static "css/2-layout/navbar.css" %}',
    '{% static "css/3-components/ui-components.css" %}',
    '{% static "js/1-core/base.js" %}',
    '{% static "js/1-core/utils.js" %}',
];

// ── Install: pre-cache core assets ──────────────────────────────────────────
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// ── Activate: remove old caches ──────────────────────────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_VERSION && key !== STATIC_CACHE)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// ── Fetch: strategy per request type ────────────────────────────────────────
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Only handle same-origin requests
    if (url.origin !== location.origin) return;

    // Skip non-GET, cart/checkout/admin/accounts (always need server)
    if (request.method !== 'GET') return;
    if (/^\/(cart|checkout|admin|accounts|profile|notifications)/.test(url.pathname)) return;

    // Static assets → cache-first
    if (/^\/(static|media)\//.test(url.pathname)) {
        event.respondWith(cacheFirst(request));
        return;
    }

    // Pages → network-first with offline fallback
    event.respondWith(networkFirstWithOfflineFallback(request));
});

// Cache-first: serve from cache, fetch and update cache if missing
async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        return new Response('', { status: 408 });
    }
}

// Network-first: try network, fall back to offline page on failure
async function networkFirstWithOfflineFallback(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_VERSION);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        const cached = await caches.match(request);
        if (cached) return cached;
        return caches.match('/offline/');
    }
}
