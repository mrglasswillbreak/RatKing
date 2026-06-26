'use client';
import dynamic from 'next/dynamic';
import { useEffect, useMemo, useRef, useState } from 'react';
import { UpdateToast } from '@/features/updates/components/update-toast';
import { InstructionSheet } from './instruction-sheet';
import { bearingBetween, calculateRoute, campusNodes, type Coordinate } from '../lib/graph';

const MapView = dynamic(() => import('@/features/map/components/map-view').then((mod) => mod.MapView), { ssr: false });
const INITIAL_POSITION: Coordinate = [3.1888, 6.4654];
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export function CampusNavigator() {
  const [destinationId, setDestinationId] = useState(campusNodes[2].id);
  const [position, setPosition] = useState<Coordinate>(INITIAL_POSITION);
  const [heading, setHeading] = useState(0);
  const [follow, setFollow] = useState(true);
  const lastPosition = useRef<Coordinate>(INITIAL_POSITION);
  const route = useMemo(() => calculateRoute(position, destinationId), [position, destinationId]);

  useEffect(() => {
    if (!navigator.geolocation) return;
    const watchId = navigator.geolocation.watchPosition((gps) => {
      const next: Coordinate = [gps.coords.longitude, gps.coords.latitude];
      setHeading((current) => gps.coords.heading ?? bearingBetween(lastPosition.current, next) ?? current);
      setPosition((current) => {
        const smoothed: Coordinate = [lerp(current[0], next[0], 0.35), lerp(current[1], next[1], 0.35)];
        lastPosition.current = smoothed;
        return smoothed;
      });
    }, undefined, { enableHighAccuracy: true, maximumAge: 3000, timeout: 10000 });
    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  return <main className="relative h-[100dvh] w-full overflow-hidden bg-slate-100 dark:bg-slate-950">
    <MapView route={[position, ...route.coordinates]} userPosition={position} heading={heading} follow={follow} />
    <div className="pointer-events-none absolute inset-x-0 top-0 z-[1] h-28 bg-gradient-to-b from-white/70 to-transparent dark:from-slate-950/70" />
    <UpdateToast />
    <InstructionSheet steps={route.steps} destinationId={destinationId} onDestinationChange={setDestinationId} follow={follow} onFollowToggle={() => setFollow((value) => !value)} />
  </main>;
}
