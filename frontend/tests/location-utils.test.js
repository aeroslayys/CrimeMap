import test from 'node:test';
import assert from 'node:assert/strict';
import {
  validIncidentPosition, suggestDemoZone, locationFieldsForPin,
} from '../src/modules/incidents/location-utils.js';

test('explicit finite map positions are accepted, including zero', () => {
  assert.equal(validIncidentPosition(11.9345, 79.8302), true);
  assert.equal(validIncidentPosition(0, 0), true);
  assert.equal(validIncidentPosition(-90, -180), true);
  assert.equal(validIncidentPosition(90, 180), true);
});

test('missing, coerced or out-of-range coordinates cannot be saved', () => {
  for (const [latitude, longitude] of [
    [null, null], [undefined, undefined], ['', ''],
    ['11.93', '79.83'], [NaN, 79.83], [Infinity, 79.83],
    [11.93, -Infinity], [90.1, 70], [-90.1, 70],
    [11.93, 180.1], [11.93, -180.1],
  ]) {
    assert.equal(validIncidentPosition(latitude, longitude), false, JSON.stringify([latitude, longitude]));
  }
});


test('pin location maps to the same illustrative polygon used by geospatial intelligence', () => {
  assert.equal(suggestDemoZone(12.031256, 79.863972), 'Demo Zone A'); // Kalapet
  assert.equal(suggestDemoZone(11.936242, 79.827969), 'Demo Zone B'); // town centre
  assert.equal(suggestDemoZone(11.894870, 79.807590), 'Demo Zone C'); // Ariyankuppam
  assert.equal(suggestDemoZone(11.912719, 79.755164), 'Demo Zone D'); // Villianur
  assert.equal(suggestDemoZone(11.935, 79.830), 'Demo Zone B');
  assert.equal(suggestDemoZone(11.9308, 79.8062), 'Demo Zone D');
});

test('no zone is guessed for missing, invalid, or distant coordinates', () => {
  for (const coordinates of [
    [null, null], ['11.935', '79.83'], [Number.NaN, 79.83],
    [11.935, 181], [0, 0], [12.15, 79.83], [11.935, 80.2],
  ]) {
    assert.equal(suggestDemoZone(...coordinates), '', String(coordinates));
  }
});

test('every new pin position replaces the previous demo zone and preserves other fields', () => {
  const previous = {
    category: 'Theft', status: 'reported', description: 'Synthetic example',
    latitude: null, longitude: null, police_station: '',
  };
  const zoneA = locationFieldsForPin(previous, 11.9573, 79.8227);
  assert.equal(zoneA.police_station, 'Demo Zone A');
  const edited = { ...zoneA, police_station: 'My manual demonstration zone' };
  const zoneB = locationFieldsForPin(edited, 11.9362, 79.8280);
  assert.equal(zoneB.police_station, 'Demo Zone B');
  assert.equal(zoneB.category, 'Theft');
  assert.equal(zoneB.description, previous.description);
  assert.deepEqual(previous, {
    category: 'Theft', status: 'reported', description: 'Synthetic example',
    latitude: null, longitude: null, police_station: '',
  });
});

test('moving outside demo coverage clears the zone; clearing pin removes stale values', () => {
  const selected = locationFieldsForPin({ category: 'Other', police_station: 'old' }, 11.9051, 79.8086);
  assert.equal(selected.police_station, 'Demo Zone C');
  const distant = locationFieldsForPin(selected, 12.15, 79.83);
  assert.equal(distant.police_station, '');
  assert.equal(distant.latitude, 12.15);
  const cleared = locationFieldsForPin(
    { ...selected, police_station: 'Manually edited zone' }, null, null,
  );
  assert.equal(cleared.latitude, null);
  assert.equal(cleared.longitude, null);
  assert.equal(cleared.police_station, '');
});

