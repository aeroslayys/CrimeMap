// Hand-drawn DEMONSTRATION sectors for map exploration only.
// These are NOT official police station limits or administrative boundaries.
// Geometry uses GeoJSON longitude/latitude coordinate order.
export const DEMO_ZONES = [
  {
    id: 'Demo Zone A', short: 'Zone A', area: 'North & northeast',
    coverage: 'Muthialpet / Lawspet → Kuilapalayam / Kalapet',
    extent: '11.945–12.037° N · 79.810–79.869° E', color: '#70b8ff',
    ring: [[79.810,11.945],[79.869,11.945],[79.869,12.037],[79.810,12.037],[79.810,11.945]],
  },
  {
    id: 'Demo Zone B', short: 'Zone B', area: 'Central / eastern city',
    coverage: 'Nellithoppe / Orleanpet → Grand Bazaar / town center',
    extent: '11.925–11.945° N · 79.809–79.846° E', color: '#d8ae69',
    ring: [[79.809,11.925],[79.846,11.925],[79.846,11.945],[79.809,11.945],[79.809,11.925]],
  },
  {
    id: 'Demo Zone C', short: 'Zone C', area: 'South / southeast',
    coverage: 'Mudaliarpet → Murungapakkam / Ariyankuppam → Nallavadu',
    extent: '11.847–11.925° N · 79.797–79.845° E (irregular)', color: '#78d7a1',
    ring: [[79.809,11.925],[79.845,11.925],[79.823,11.847],[79.797,11.847],[79.798,11.890],[79.809,11.925]],
  },
  {
    id: 'Demo Zone D', short: 'Zone D', area: 'West / southwest',
    coverage: 'Mettupalayam / Reddiarpalayam → Villianur / Mangalam / Karikalampakkam',
    extent: '11.847–11.952° N · 79.731–79.809° E (irregular)', color: '#cfa2e8',
    ring: [[79.731,11.952],[79.809,11.952],[79.809,11.925],[79.798,11.890],[79.797,11.847],[79.731,11.847],[79.731,11.952]],
  },
];

export function isWithinZone(latitude, longitude, zone) {
  // Ray casting makes selection depend on geography, not editable station text.
  const ring = zone.ring;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if ((yi > latitude) !== (yj > latitude) &&
        longitude < ((xj - xi) * (latitude - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

export function zoneForPoint(latitude, longitude) {
  return DEMO_ZONES.find(zone => isWithinZone(latitude, longitude, zone)) || null;
}

export function zoneBounds(zone) {
  return zone.ring.map(([longitude, latitude]) => [latitude, longitude]);
}
