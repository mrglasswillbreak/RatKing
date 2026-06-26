import { defaultCache } from '@serwist/next/worker';
import { CacheFirst, ExpirationPlugin, Serwist, StaleWhileRevalidate } from 'serwist';

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  runtimeCaching: [
    ...defaultCache,
    { matcher: ({ url }) => url.pathname.startsWith('/map-data/') || url.pathname.endsWith('.pmtiles'), handler: new CacheFirst({ cacheName: 'lasu-map-assets', plugins: [new ExpirationPlugin({ maxEntries: 5000, maxAgeSeconds: 60 * 60 * 24 * 365 })] }) },
    { matcher: ({ request }) => request.destination === 'document', handler: new StaleWhileRevalidate({ cacheName: 'lasu-app-shell' }) }
  ]
});

serwist.addEventListeners();
