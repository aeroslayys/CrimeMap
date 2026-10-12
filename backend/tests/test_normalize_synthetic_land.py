import csv
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.demo_land import demo_position, in_demo_land
from app.models import Incident
from app.operations import overview
from scripts.normalize_synthetic_land import normalize


def test_all_synthetic_rows_corrected_preserving_metadata_and_repeat_safe(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'land.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        for identifier, source, lat, lon in [
            ('DEMO-0001', 'synthetic', 11.95, 79.86),
            ('imported-uuid', 'synthetic', 11.96, 79.86),
            ('inland-custom', 'synthetic', 11.9325, 79.811),
            ('real-record', 'official', 11.96, 79.86),
        ]:
            db.add(Incident(id=identifier, source_type=source, latitude=lat, longitude=lon,
                            category='Other', occurred_at='2026-10-12T10:00:00Z',
                            police_station='Custom zone', description='Edited note', status='closed'))
        db.commit()
        before = {r.id: {c.name: getattr(r, c.name) for c in Incident.__table__.columns}
                  for r in db.scalars(select(Incident))}
    preview = normalize(session_factory=factory)
    assert preview == {'synthetic_total': 3, 'changed': 2, 'already_inland': 1, 'non_synthetic_untouched': 1}
    with factory() as db:
        assert db.get(Incident, 'DEMO-0001').longitude == 79.86
    assert normalize(apply=True, session_factory=factory) == preview
    with factory() as db:
        for record in db.scalars(select(Incident)):
            if record.source_type == 'synthetic':
                assert in_demo_land(record.latitude, record.longitude)
            for key, value in before[record.id].items():
                if key not in ('latitude', 'longitude') or record.id in ('real-record', 'inland-custom'):
                    assert getattr(record, key) == value
    assert normalize(apply=True, session_factory=factory)['changed'] == 0
    engine.dispose()


def test_bundled_fixtures_and_all_operational_points_stay_inland():
    root = Path(__file__).resolve().parents[2]
    for path in [root / 'data/synthetic_incidents.csv', root / 'frontend/public/sample-data/synthetic_incidents.csv']:
        with path.open() as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 100
        assert all(in_demo_land(float(r['latitude']), float(r['longitude'])) for r in rows)
    data = overview()
    for point in data['cameras'] + data['accidents']:
        assert in_demo_land(point['latitude'], point['longitude'])
    for patrol in data['patrols']:
        for start, end in zip(patrol['track'], patrol['track'][1:]):
            for i in range(101):
                assert in_demo_land(start['latitude'] + (end['latitude'] - start['latitude']) * i / 100,
                                    start['longitude'] + (end['longitude'] - start['longitude']) * i / 100)


def test_generated_positions_are_stable_and_bounded():
    for index in range(1000):
        point = demo_position(str(index), 'Unknown imported zone')
        assert in_demo_land(*point)
        assert point == demo_position(str(index), 'Unknown imported zone')
    assert not in_demo_land(11.95, 79.86)
    assert not in_demo_land(float('nan'), 79.811)
