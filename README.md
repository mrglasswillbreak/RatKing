# LASU Campus Navigator PWA

Offline-first Apple Maps inspired campus navigation PWA for LASU Ojo built with Next.js 15, TypeScript, Tailwind CSS, Framer Motion, MapLibre GL JS, PMTiles, Serwist, and IndexedDB.

## Proposed feature-based structure

- `src/app`: App Router shell, global styles, Serwist worker entry.
- `src/features/map`: MapLibre/PMTiles map rendering.
- `src/features/navigation`: local campus graph, A* routing, follow camera, animated instruction sheet.
- `src/features/offline`: service worker registration and IndexedDB tile/version helpers.
- `src/features/theme`: system-aware light/dark theming.
- `src/features/updates`: map-pack version checks and update toast.

## Local development

```bash
npm install
npm run dev
```

For production, add a LASU Ojo PMTiles extract at `public/map-data/lasu-ojo.pmtiles`, then run:

```bash
npm run build
npm start
```
