'use client';
import { DownloadCloud, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getMapVersion, saveMapVersion } from '@/features/offline/lib/tile-cache';

type VersionInfo = { version: string; sizeMb: number; pmtilesUrl: string };

export function UpdateToast() {
  const [info, setInfo] = useState<VersionInfo | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => { void (async () => {
    try {
      const remote = await fetch('/version.json', { cache: 'no-store' }).then((res) => res.json()) as VersionInfo;
      const local = await getMapVersion();
      if (remote.version !== local) setInfo(remote);
    } catch { /* app remains offline-first when version endpoint is unavailable */ }
  })(); }, []);
  if (!info) return null;
  return <div className="absolute left-4 right-4 top-4 z-20 rounded-3xl bg-slate-950/90 p-4 text-white shadow-glass">
    <button className="absolute right-3 top-3" onClick={() => setInfo(null)}><X size={18} /></button>
    <div className="flex items-center gap-3 pr-5"><DownloadCloud className="text-brand-50" /><div><p className="font-semibold">Offline map update available</p><p className="text-sm text-white/70">Version {info.version} · about {info.sizeMb}MB. Download when connected to Wi‑Fi.</p></div></div>
    <button disabled={busy} onClick={async () => { setBusy(true); await saveMapVersion(info.version); setBusy(false); setInfo(null); }} className="mt-3 rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold disabled:opacity-50">{busy ? 'Preparing…' : 'Download / Update Map'}</button>
  </div>;
}
