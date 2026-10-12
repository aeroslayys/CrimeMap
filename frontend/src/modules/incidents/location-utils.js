import { zoneForPoint } from '../map/demo-zones.js';

/** Shared form safeguard: only finite, explicitly selected geographic coordinates. */
export function validIncidentPosition(latitude, longitude) {
  return typeof latitude === 'number' && Number.isFinite(latitude) &&
    typeof longitude === 'number' && Number.isFinite(longitude) &&
    latitude >= -90 && latitude <= 90 &&
    longitude >= -180 && longitude <= 180;
}

/** Match the visible demonstration polygons, never an old nearest-cluster guess. */
export function suggestDemoZone(latitude, longitude) {
  if (!validIncidentPosition(latitude, longitude)) return '';
  return zoneForPoint(latitude, longitude)?.id || '';
}

/** Update every location-related field together so an earlier label does not linger. */
export function locationFieldsForPin(previous, latitude, longitude) {
  if (!validIncidentPosition(latitude, longitude)) {
    return { ...previous, latitude: null, longitude: null, police_station: '' };
  }
  return { ...previous, latitude, longitude,
    police_station: suggestDemoZone(latitude, longitude) };
}
