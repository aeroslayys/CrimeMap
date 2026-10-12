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


test('each boundary has an explicit geographic from/to description and accurate limits', () => {
  const names = new Set();
  for (const zone of DEMO_ZONES) {
    assert.ok(zone.from && zone.to && zone.from !== zone.to);
    assert.ok(zone.direction);
    assert.ok(zone.coverage.includes('→'));
    for (const reference of [zone.startReference, zone.endReference]) {
      assert.ok(reference.label);
      assert.ok(isWithinZone(reference.latitude, reference.longitude, zone),
        `${zone.id} has an indicative reference point outside its own polygon`);
    }
    assert.ok(!names.has(zone.short));
    names.add(zone.short);
    assert.deepEqual(zone.ring[0], zone.ring.at(-1), 'Polygon must be a closed ring');
    const latitudes = zone.ring.map(([, latitude]) => latitude);
    const longitudes = zone.ring.map(([longitude]) => longitude);
    for (const limit of [
      Math.min(...latitudes), Math.max(...latitudes),
      Math.min(...longitudes), Math.max(...longitudes),
    ]) {
      assert.ok(zone.extent.includes(limit.toFixed(3)),
        `${zone.id}: extent does not describe polygon coordinate ${limit.toFixed(3)}`);
    }
  }
});
