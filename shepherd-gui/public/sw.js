/**
 * Service Worker for Shepherd GUI
 * Phase 7: Performance Optimization & Polish
 * Implements intelligent caching strategy
 */

const CACHE_NAME = 'shepherd-gui-v1'
const STATIC_CACHE = 'shepherd-static-v1'
const DYNAMIC_CACHE = 'shepherd-dynamic-v1'

// Assets to precache
const PRECACHE_URLS = [
  '/',
  '/Shepherd.png',
  '/_next/static/css/',
  '/_next/static/js/'
]

// Cache strategies by resource type
const CACHE_STRATEGIES = {
  // Static assets - Cache First
  static: [
    /\/_next\/static\//,
    /\.(?:js|css|woff2?|png|jpg|jpeg|gif|svg|ico)$/,
  ],
  
  // API calls - Network First
  api: [
    /\/api\//,
    /\/ws/
  ],
  
  // Pages - Stale While Revalidate
  pages: [
    /^\/$/,
    /^\/[^\/]+$/
  ]
}

// Install event - precache critical assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...')
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Precaching static assets')
        return cache.addAll(PRECACHE_URLS)
      })
      .then(() => {
        console.log('[SW] Installation complete')
        return self.skipWaiting()
      })
      .catch((error) => {
        console.error('[SW] Installation failed:', error)
      })
  )
})

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== CACHE_NAME && 
                     cacheName !== STATIC_CACHE && 
                     cacheName !== DYNAMIC_CACHE
            })
            .map((cacheName) => {
              console.log('[SW] Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            })
        )
      })
      .then(() => {
        console.log('[SW] Activation complete')
        return self.clients.claim()
      })
  )
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }
  
  // Skip cross-origin requests (except for known CDNs)
  if (url.origin !== location.origin && !isTrustedOrigin(url.origin)) {
    return
  }
  
  // Determine cache strategy
  const strategy = getCacheStrategy(request.url)
  
  switch (strategy) {
    case 'static':
      event.respondWith(cacheFirst(request))
      break
    case 'api':
      event.respondWith(networkFirst(request))
      break
    case 'pages':
      event.respondWith(staleWhileRevalidate(request))
      break
    default:
      event.respondWith(networkFirst(request))
  }
})

// Cache First Strategy - for static assets
async function cacheFirst(request) {
  try {
    const cached = await caches.match(request)
    if (cached) {
      return cached
    }
    
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE)
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    console.error('[SW] Cache first failed:', error)
    return new Response('Network error', { status: 503 })
  }
}

// Network First Strategy - for API calls
async function networkFirst(request) {
  try {
    const response = await fetch(request)
    
    if (response.ok && !isWebSocket(request)) {
      const cache = await caches.open(DYNAMIC_CACHE)
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url)
    
    const cached = await caches.match(request)
    if (cached) {
      return cached
    }
    
    return new Response(
      JSON.stringify({ error: 'Network unavailable' }), 
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

// Stale While Revalidate Strategy - for pages
async function staleWhileRevalidate(request) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE)
    const cached = await cache.match(request)
    
    // Fetch fresh version in background
    const fetchPromise = fetch(request).then((response) => {
      if (response.ok) {
        cache.put(request, response.clone())
      }
      return response
    })
    
    // Return cached version immediately, or wait for network
    return cached || await fetchPromise
  } catch (error) {
    console.error('[SW] Stale while revalidate failed:', error)
    const cached = await caches.match(request)
    return cached || new Response('Page unavailable', { status: 503 })
  }
}

// Helper functions
function getCacheStrategy(url) {
  if (CACHE_STRATEGIES.static.some(pattern => pattern.test(url))) {
    return 'static'
  }
  if (CACHE_STRATEGIES.api.some(pattern => pattern.test(url))) {
    return 'api'
  }
  if (CACHE_STRATEGIES.pages.some(pattern => pattern.test(url))) {
    return 'pages'
  }
  return 'default'
}

function isTrustedOrigin(origin) {
  const trustedOrigins = [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://cdn.jsdelivr.net'
  ]
  return trustedOrigins.includes(origin)
}

function isWebSocket(request) {
  return request.url.includes('/ws') || 
         request.headers.get('upgrade') === 'websocket'
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync())
  }
})

async function handleBackgroundSync() {
  console.log('[SW] Handling background sync')
  // Implement offline action replay here
}

// Push notifications (for future use)
self.addEventListener('push', (event) => {
  if (!event.data) return
  
  const options = {
    body: event.data.text(),
    icon: '/Shepherd.png',
    badge: '/Shepherd.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '2'
    },
    actions: [
      {
        action: 'explore',
        title: 'Open App',
        icon: '/Shepherd.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/Shepherd.png'
      }
    ]
  }
  
  event.waitUntil(
    self.registration.showNotification('Shepherd Update', options)
  )
})

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    )
  }
})