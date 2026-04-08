{% load static %}
const CACHE_VERSION = 'hendoshi-v1';
const STATIC_CACHE = 'hendoshi-static-v1';
const OFFLINE_URL = '/offline/';

// Optional assets to cache on install — failures are silently ignored
const OPTIONAL_CACHE_URLS = [
    '{% static "images/icons/icon-192.png" %}',
    '{% static "images/icons/icon-512.png" %}',
    '{% static "images/pug-skull.webp" %}',
    '{% static "css/1-foundation/variables.css" %}',
    '{% static "css/2-layout/navbar.css" %}',
    '{% static "css/3-components/ui-components.css" %}',
    '{% static "js/1-core/base.js" %}',
    '{% static "js/1-core/utils.js" %}',
];

// ── Install: cache offline page first (critical), then others best-effort ──
self.addEventListener('install', event => {
    event.waitUntil(
        (async () => {
            const cache = await caches.open(STATIC_CACHE);
            // Offline page MUST be cached — fail install if it can't be fetched
            await cache.add(OFFLINE_URL);
            // Everything else is best-effort — a single failure won't block install
            await Promise.allSettled(
                OPTIONAL_CACHE_URLS.map(url =>
                    cache.add(url).catch(() => { /* ignore */ })
                )
            );
            await self.skipWaiting();
        })()
    );
});

// ── Activate: remove stale caches ────────────────────────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(
                keys
                    .filter(key => key !== CACHE_VERSION && key !== STATIC_CACHE)
                    .map(key => caches.delete(key))
            ))
            .then(() => self.clients.claim())
    );
});

// ── Fetch: strategy per request type ─────────────────────────────────────────
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Only handle same-origin GET requests
    if (url.origin !== location.origin) return;
    if (request.method !== 'GET') return;

    // Skip pages that always need the server
    if (/^\/(cart|checkout|admin|accounts|profile|notifications)/.test(url.pathname)) return;

    // Static & media assets → cache-first
    if (/^\/(static|media)\//.test(url.pathname)) {
        event.respondWith(cacheFirst(request));
        return;
    }

    // All other pages → network-first with offline fallback
    event.respondWith(networkFirstWithOfflineFallback(request));
});

// Cache-first: return cached copy instantly; fetch + update cache if missing
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
        return new Response('Asset unavailable offline', { status: 408 });
    }
}

// Network-first: try network → fall back to cache → fall back to offline page
async function networkFirstWithOfflineFallback(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_VERSION);
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        // Try cached version of this specific page
        const cached = await caches.match(request);
        if (cached) return cached;
        // Last resort: show branded offline page
        const offlinePage = await caches.match(OFFLINE_URL);
        if (offlinePage) return offlinePage;
        // Absolute fallback if offline page itself isn't cached somehow
        return new Response(
            '<h1 style="font-family:sans-serif;text-align:center;padding:4rem">You are offline</h1>',
            { status: 503, headers: { 'Content-Type': 'text/html' } }
        );
    }
}
