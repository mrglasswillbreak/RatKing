import { openDB } from 'idb';

const DB_NAME = 'lasu-offline-map';
const TILE_STORE = 'tiles';
const META_STORE = 'metadata';

export async function getOfflineDb() {
  return openDB(DB_NAME, 1, { upgrade(db) { db.createObjectStore(TILE_STORE); db.createObjectStore(META_STORE); } });
}

export async function cacheTile(url: string, response: ArrayBuffer) {
  const db = await getOfflineDb();
  await db.put(TILE_STORE, response, url);
}

export async function readCachedTile(url: string) {
  const db = await getOfflineDb();
  return db.get(TILE_STORE, url) as Promise<ArrayBuffer | undefined>;
}

export async function saveMapVersion(version: string) {
  const db = await getOfflineDb();
  await db.put(META_STORE, version, 'mapVersion');
}

export async function getMapVersion() {
  const db = await getOfflineDb();
  return (await db.get(META_STORE, 'mapVersion')) as string | undefined;
}
