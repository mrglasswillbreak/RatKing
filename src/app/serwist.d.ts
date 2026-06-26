import type { PrecacheEntry } from 'serwist';

declare global {
  interface WorkerGlobalScope { __SW_MANIFEST: (PrecacheEntry | string)[]; }
  const self: WorkerGlobalScope & typeof globalThis;
}
