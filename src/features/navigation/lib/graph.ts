export type Coordinate = [number, number];
export type CampusNode = { id: string; name: string; coordinate: Coordinate };
export type CampusEdge = { from: string; to: string; distance: number; instruction: string };
export type RouteStep = { text: string; distance: number; coordinate: Coordinate };

export const campusNodes: CampusNode[] = [
  { id: 'main_gate', name: 'Main Gate', coordinate: [3.1888, 6.4654] },
  { id: 'library', name: 'University Library', coordinate: [3.1902, 6.4666] },
  { id: 'science', name: 'Faculty of Science', coordinate: [3.1916, 6.4673] },
  { id: 'senate', name: 'Senate Building', coordinate: [3.1895, 6.4681] },
  { id: 'student_arcade', name: 'Student Arcade', coordinate: [3.1923, 6.4661] }
];

export const campusEdges: CampusEdge[] = [
  { from: 'main_gate', to: 'library', distance: 220, instruction: 'Head north-east from Main Gate towards the Library.' },
  { from: 'library', to: 'science', distance: 180, instruction: 'In 180m, continue towards Faculty of Science.' },
  { from: 'library', to: 'senate', distance: 210, instruction: 'Turn left towards Senate Building.' },
  { from: 'science', to: 'student_arcade', distance: 160, instruction: 'In 160m, turn right towards Student Arcade.' },
  { from: 'senate', to: 'science', distance: 260, instruction: 'Continue east towards Faculty of Science.' }
];

function heuristic(a: CampusNode, b: CampusNode) {
  const dx = (a.coordinate[0] - b.coordinate[0]) * 111_320;
  const dy = (a.coordinate[1] - b.coordinate[1]) * 110_540;
  return Math.hypot(dx, dy);
}

export function findNearestNode(coordinate: Coordinate) {
  return campusNodes.reduce((best, node) => heuristic({ ...node, coordinate }, node) < heuristic({ ...best, coordinate }, best) ? node : best, campusNodes[0]);
}

export function calculateRoute(startCoordinate: Coordinate, destinationId: string) {
  const start = findNearestNode(startCoordinate);
  const destination = campusNodes.find((node) => node.id === destinationId) ?? campusNodes[1];
  const open = new Set([start.id]);
  const cameFrom = new Map<string, string>();
  const gScore = new Map(campusNodes.map((node) => [node.id, Number.POSITIVE_INFINITY]));
  const fScore = new Map(campusNodes.map((node) => [node.id, Number.POSITIVE_INFINITY]));
  gScore.set(start.id, 0); fScore.set(start.id, heuristic(start, destination));

  while (open.size) {
    const current = [...open].sort((a, b) => (fScore.get(a) ?? 0) - (fScore.get(b) ?? 0))[0];
    if (current === destination.id) break;
    open.delete(current);
    for (const edge of campusEdges.filter((edge) => edge.from === current || edge.to === current)) {
      const neighbor = edge.from === current ? edge.to : edge.from;
      const tentative = (gScore.get(current) ?? 0) + edge.distance;
      if (tentative < (gScore.get(neighbor) ?? Infinity)) {
        cameFrom.set(neighbor, current); gScore.set(neighbor, tentative);
        fScore.set(neighbor, tentative + heuristic(campusNodes.find((node) => node.id === neighbor)!, destination));
        open.add(neighbor);
      }
    }
  }

  const path = [destination.id];
  while (cameFrom.has(path[0])) path.unshift(cameFrom.get(path[0])!);
  const coordinates = path.map((id) => campusNodes.find((node) => node.id === id)!.coordinate);
  const steps: RouteStep[] = path.slice(1).map((id, index) => {
    const edge = campusEdges.find((edge) => (edge.from === path[index] && edge.to === id) || (edge.to === path[index] && edge.from === id));
    return { text: edge?.instruction ?? `Continue to ${id}.`, distance: edge?.distance ?? 0, coordinate: campusNodes.find((node) => node.id === id)!.coordinate };
  });
  return { start, destination, coordinates, steps, distance: gScore.get(destination.id) ?? 0 };
}

export function bearingBetween(a: Coordinate, b: Coordinate) {
  const toRad = Math.PI / 180, toDeg = 180 / Math.PI;
  const [lon1, lat1] = a.map((value) => value * toRad);
  const [lon2, lat2] = b.map((value) => value * toRad);
  const y = Math.sin(lon2 - lon1) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
  return (Math.atan2(y, x) * toDeg + 360) % 360;
}
