'use client';

import maplibregl, { Map } from 'maplibre-gl';
import { Protocol } from 'pmtiles';
import { useEffect, useRef } from 'react';
import type { Coordinate } from '@/features/navigation/lib/graph';

type MapViewProps = { route: Coordinate[]; userPosition: Coordinate; heading: number; follow: boolean };

export function MapView({ route, userPosition, heading, follow }: MapViewProps) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);

  useEffect(() => {
    if (!container.current || mapRef.current) return;
    const protocol = new Protocol();
    maplibregl.addProtocol('pmtiles', protocol.tile);
    const map = new maplibregl.Map({
      container: container.current,
      center: userPosition,
      zoom: 16,
      pitch: 40,
      bearing: -12,
      style: {
        version: 8,
        sources: {
          lasu: { type: 'vector', url: 'pmtiles:///map-data/lasu-ojo.pmtiles', attribution: '© OpenStreetMap contributors' },
          campusFallback: { type: 'geojson', data: '/map-data/lasu-fallback.geojson' }
        },
        layers: [
          { id: 'background', type: 'background', paint: { 'background-color': '#eaf3ff' } },
          { id: 'landuse', type: 'fill', source: 'lasu', 'source-layer': 'landuse', paint: { 'fill-color': '#dff4df', 'fill-opacity': 0.75 } },
          { id: 'roads', type: 'line', source: 'lasu', 'source-layer': 'transportation', paint: { 'line-color': '#ffffff', 'line-width': 4 } },
          { id: 'fallback-green', type: 'fill', source: 'campusFallback', filter: ['==', ['get', 'kind'], 'green'], paint: { 'fill-color': '#dff4df', 'fill-opacity': 0.85 } },
          { id: 'fallback-roads', type: 'line', source: 'campusFallback', filter: ['==', ['get', 'kind'], 'road'], paint: { 'line-color': '#ffffff', 'line-width': 5 } },
          { id: 'fallback-buildings', type: 'fill', source: 'campusFallback', filter: ['==', ['get', 'kind'], 'building'], paint: { 'fill-color': '#f7d7b5', 'fill-opacity': 0.9 } },
          { id: 'buildings', type: 'fill', source: 'lasu', 'source-layer': 'building', paint: { 'fill-color': '#f7d7b5', 'fill-opacity': 0.9 } }
        ]
      }
    });
    mapRef.current = map;
    const element = document.createElement('div');
    element.innerHTML = '<svg class="pulse-marker" viewBox="0 0 40 40"><circle cx="20" cy="20" r="18" fill="#0a84ff" opacity=".18"><animate attributeName="r" values="10;18;10" dur="1.8s" repeatCount="indefinite"/></circle><path d="M20 4 31 32 20 26 9 32Z" fill="#0a84ff" stroke="white" stroke-width="3"/></svg>';
    markerRef.current = new maplibregl.Marker({ element }).setLngLat(userPosition).addTo(map);
    return () => { markerRef.current?.remove(); map.remove(); maplibregl.removeProtocol('pmtiles'); mapRef.current = null; };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const draw = () => {
      const data = { type: 'Feature', geometry: { type: 'LineString', coordinates: route }, properties: {} } as GeoJSON.Feature<GeoJSON.LineString>;
      if (map.getSource('active-route')) (map.getSource('active-route') as maplibregl.GeoJSONSource).setData(data);
      else {
        map.addSource('active-route', { type: 'geojson', data });
        map.addLayer({ id: 'active-route-glow', type: 'line', source: 'active-route', paint: { 'line-color': '#0a84ff', 'line-width': 12, 'line-opacity': 0.22 } });
        map.addLayer({ id: 'active-route', type: 'line', source: 'active-route', paint: { 'line-color': '#0a84ff', 'line-width': 6, 'line-cap': 'round', 'line-join': 'round' } });
      }
    };
    if (map.loaded()) draw(); else map.once('load', draw);
  }, [route]);

  useEffect(() => {
    markerRef.current?.setLngLat(userPosition);
    const svg = markerRef.current?.getElement().querySelector('svg');
    if (svg) svg.setAttribute('style', `transform: rotate(${heading}deg)`);
    if (follow) mapRef.current?.easeTo({ center: userPosition, bearing: heading, duration: 900 });
  }, [userPosition, heading, follow]);

  return <div ref={container} className="absolute inset-0" aria-label="LASU Ojo campus map" />;
}
