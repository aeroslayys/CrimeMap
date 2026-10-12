"""Administrator can explicitly spread only untouched canonical fictional DEMO locations."""
import csv

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.main as main_module
from app.auth import COOKIE
from app.models import Incident
from scripts.reposition_demo import CSV, PREVIOUS


def old_points():
    with PREVIOUS.open(newline="", encoding="utf-8") as stream:
        return {row["id"]: (float(row["old_latitude"]), float(row["old_longitude"]))
                for row in csv.DictReader(stream)}


def target_points():
    with CSV.open(newline="", encoding="utf-8") as stream:
        return {row["id"]: (float(row["latitude"]), float(row["longitude"]))
                for row in csv.DictReader(stream)}


def seed_example(db, identifier, location, *, source="synthetic", status="closed"):
    db.add(Incident(
        id=identifier, category="Theft", occurred_at="2026-09-01T00:00:00Z",
        latitude=location[0], longitude=location[1],
        police_station="Demo Zone A", description="An edited note is preserved",
        status=status, source_type=source,
    ))


def test_preview_requires_confirmation_and_changes_only_unchanged_originals(client):
    old, target = old_points(), target_points()
    with Session(main_module.engine) as db:
        seed_example(db, "DEMO-0001", old["DEMO-0001"])
        seed_example(db, "DEMO-0002", (old["DEMO-0002"][0] + .008, old["DEMO-0002"][1]))
        seed_example(db, "DEMO-0003", old["DEMO-0003"], source="official")
        seed_example(db, "DEMO-0004", target["DEMO-0004"])
        seed_example(db, "CUSTOM-IMPORTED", old["DEMO-0001"])
        db.commit()

    preview = client.get("/api/admin/demo-redistribution")
    assert preview.status_code == 200, preview.text
    counts = preview.json()
    assert counts == {
        "canonical_total": 100, "ready_to_move": 1, "already_current": 1,
        "skipped_custom": 2, "missing": 96, "updated": 0,
    }
    with Session(main_module.engine) as db:
        assert (db.get(Incident, "DEMO-0001").latitude,
                db.get(Incident, "DEMO-0001").longitude) == old["DEMO-0001"]
    assert client.post("/api/admin/demo-redistribution", json={}).status_code == 422
    assert client.post("/api/admin/demo-redistribution",
                       json={"confirmation": "yes"}).status_code == 422

    applied = client.post("/api/admin/demo-redistribution",
                          json={"confirmation": "REDISTRIBUTE_CANONICAL_DEMOS"})
    assert applied.status_code == 200, applied.text
    assert applied.json()["updated"] == 1
    with Session(main_module.engine) as db:
        record = db.get(Incident, "DEMO-0001")
        assert (record.latitude, record.longitude) == target["DEMO-0001"]
        assert record.status == "closed"
        assert record.description == "An edited note is preserved"
        assert (db.get(Incident, "DEMO-0002").latitude, db.get(Incident, "DEMO-0002").longitude) == (
            old["DEMO-0002"][0] + .008, old["DEMO-0002"][1])
        assert (db.get(Incident, "DEMO-0003").latitude, db.get(Incident, "DEMO-0003").longitude) == old["DEMO-0003"]
        assert (db.get(Incident, "CUSTOM-IMPORTED").latitude,
                db.get(Incident, "CUSTOM-IMPORTED").longitude) == old["DEMO-0001"]
    audit = client.get("/api/admin/audit").json()
    assert audit["total"] == 1
    assert audit["items"][0]["action"] == "incident.demo_redistributed"
    assert audit["items"][0]["details"]["updated"] == 1
    assert client.post("/api/admin/demo-redistribution",
                       json={"confirmation": "REDISTRIBUTE_CANONICAL_DEMOS"}).json()["updated"] == 0
    assert client.get("/api/admin/audit").json()["total"] == 1


def test_demo_redistribution_requires_admin_role(client):
    assert client.post("/api/admin/users", json={
        "username": "demoviewer", "password": "strong-password-example", "role": "viewer",
    }).status_code == 201
    client.cookies.delete(COOKIE)
    assert client.get("/api/admin/demo-redistribution").status_code == 401
    assert client.post("/api/admin/demo-redistribution",
                       json={"confirmation": "REDISTRIBUTE_CANONICAL_DEMOS"}).status_code == 401
    assert client.post("/api/auth/login",
                       json={"username": "demoviewer", "password": "strong-password-example"}).status_code == 200
    assert client.get("/api/admin/demo-redistribution").status_code == 403
    assert client.post("/api/admin/demo-redistribution",
                       json={"confirmation": "REDISTRIBUTE_CANONICAL_DEMOS"}).status_code == 403
