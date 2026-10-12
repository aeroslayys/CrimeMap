import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DEMO_ZONES, isWithinZone, zoneForPoint } from '../src/modules/map/demo-zones.js';

const fixtureUrl = new URL('../public/sample-data/synthetic_incidents.csv', import.meta.url);
const [header, ...records] = readFileSync(fixtureUrl, 'utf8').trim().split(/\r?\n/);
const columns = header.split(',');
const incidents = records.map(line => Object.fromEntries(
  line.split(',').map((value, index) => [columns[index], value]),
));

test('zone geometries cover canonical fiction by point, not editable station name', () => {
  assert.equal(DEMO_ZONES.length, 4);
  assert.equal(incidents.length, 100);
  for (const record of incidents) {
    const lat = +record.latitude, lon = +record.longitude;
    const zone = zoneForPoint(lat, lon);
    assert.equal(zone?.id, record.police_station,
      `Coordinate ${lat}, ${lon} did not map to ${record.police_station}`);
    assert.equal(isWithinZone(lat, lon, zone), true);
  }
  assert.equal(zoneForPoint(13, 81), null);
});

test('seed is broadly distributed across the Puducherry demo study area', () => {
  const lat = incidents.map(row => +row.latitude);
  const lon = incidents.map(row => +row.longitude);
  assert.ok(Math.max(...lat) - Math.min(...lat) > 0.15);
  assert.ok(Math.max(...lon) - Math.min(...lon) > 0.10);
  const neighborhoods = new Set(incidents.map(row =>
    [Number(row.latitude).toFixed(2), Number(row.longitude).toFixed(2)].join(',')));
  assert.ok(neighborhoods.size >= 15);
});
