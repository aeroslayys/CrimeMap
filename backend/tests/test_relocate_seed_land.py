"""Seed-coordinate correction is opt-in and only affects matching original fixtures."""
import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models import Incident
from scripts.relocate_seed_land import MANIFEST, relocation_summary


def test_relocation_preview_then_explicit_apply_is_idempotent_and_conservative(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'land-correction-tests.db'}")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 100
    with Session(engine) as db:
        for row in rows[:3]:
            date = datetime.fromisoformat(row["occurred_at"]).astimezone(timezone.utc)
            db.add(Incident(id=row["id"], category=row["category"],
                occurred_at=date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                latitude=float(row["old_latitude"]), longitude=float(row["old_longitude"]),
                police_station=row["police_station"], description=row["description"],
                status="reported", source_type="synthetic"))
        # A manually moved seed should be ignored, not teleported to the new coordinates.
        db.add(Incident(id="CUSTOM", category="Other",
            occurred_at="2026-09-09T02:00:00Z", latitude=11.935, longitude=79.828,
            police_station="Custom", description="CUSTOM DEMO", status="closed", source_type="synthetic"))
        db.commit()
        db.get(Incident, rows[1]["id"]).latitude = 11.9000
        db.commit()

    preview = relocation_summary(session_factory=factory)
    assert preview == {"matched": 2, "already_corrected": 0, "missing": 97, "modified_or_unrecognized": 1}
    with Session(engine) as db:
        assert db.get(Incident, rows[0]["id"]).latitude == float(rows[0]["old_latitude"])
        assert db.get(Incident, "CUSTOM").latitude == 11.935

    applied = relocation_summary(apply=True, session_factory=factory)
    assert applied == preview
    with Session(engine) as db:
        assert db.get(Incident, rows[0]["id"]).latitude == float(rows[0]["new_latitude"])
        assert db.get(Incident, rows[2]["id"]).longitude == float(rows[2]["new_longitude"])
        assert db.get(Incident, rows[1]["id"]).latitude == 11.9000
        assert db.get(Incident, "CUSTOM").latitude == 11.935

    repeat = relocation_summary(apply=True, session_factory=factory)
    assert repeat == {"matched": 0, "already_corrected": 2, "missing": 97, "modified_or_unrecognized": 1}
    engine.dispose()
