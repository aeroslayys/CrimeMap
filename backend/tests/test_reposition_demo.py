"""Correction must never overwrite user-edited coordinates or modify DB by default."""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models import Incident
from scripts import reposition_demo


def test_reposition_dry_run_and_safe_apply(tmp_path, monkeypatch, capsys):
    engine = create_engine(f"sqlite:///{tmp_path / 'reposition.db'}")
    Base.metadata.create_all(engine)
    old_a = reposition_demo.LEGACY_COORDINATES["DEMO-0001"]
    old_b = reposition_demo.LEGACY_COORDINATES["DEMO-0002"]
    with Session(engine) as db:
        db.add_all([
            Incident(id="DEMO-0001", category="Theft", occurred_at="2026-09-01T00:00:00Z",
                     latitude=old_a[0], longitude=old_a[1], police_station="Demo Zone A",
                     description="edited note", status="closed", source_type="synthetic"),
            Incident(id="DEMO-0002", category="Theft", occurred_at="2026-09-01T00:00:00Z",
                     latitude=old_b[0] + 0.01, longitude=old_b[1], police_station="Demo Zone B",
                     description="user moved this pin", status="reported", source_type="synthetic"),
            Incident(id="CUSTOM-1", category="Theft", occurred_at="2026-09-01T00:00:00Z",
                     latitude=old_a[0], longitude=old_a[1], police_station="Demo Zone A",
                     description="imported row", status="reported", source_type="synthetic"),
        ])
        db.commit()
    monkeypatch.setattr(reposition_demo, "SessionLocal", sessionmaker(bind=engine))
    reposition_demo.main([])
    with Session(engine) as db:
        assert (db.get(Incident, "DEMO-0001").latitude, db.get(Incident, "DEMO-0001").longitude) == old_a
    reposition_demo.main(["--apply"])
    with Session(engine) as db:
        changed = db.get(Incident, "DEMO-0001")
        assert round(changed.longitude, 6) == 79.810400
        assert changed.description == "edited note"
        assert changed.status == "closed"
        assert (db.get(Incident, "DEMO-0002").latitude, db.get(Incident, "DEMO-0002").longitude) == (old_b[0] + .01, old_b[1])
        assert db.get(Incident, "CUSTOM-1").description == "imported row"
        assert len(db.scalars(select(Incident)).all()) == 3
    assert "SKIP DEMO-0002" in capsys.readouterr().out
    engine.dispose()
