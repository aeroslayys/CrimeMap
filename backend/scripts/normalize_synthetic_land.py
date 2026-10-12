"""Move ALL out-of-area synthetic incidents into inland demo blocks.

Includes edited and imported synthetic records. This deliberately changes even
valid inland locations outside the four demo blocks; it is NOT a water detector.
Only latitude/longitude change. Default is preview; --apply commits atomically.
"""
import argparse
import csv
import json
from pathlib import Path

from sqlalchemy import select

from app.db import SessionLocal
from app.demo_land import demo_position, in_demo_land
from app.models import Incident

CSV = Path(__file__).resolve().parents[2] / "data" / "synthetic_incidents.csv"


def normalize(*, apply=False, session_factory=None):
    with CSV.open(newline="", encoding="utf-8") as source:
        targets = {row["id"]: (float(row["latitude"]), float(row["longitude"]))
                   for row in csv.DictReader(source)}
    if not all(in_demo_land(*point) for point in targets.values()):
        raise ValueError("Bundled fixture contains a coordinate outside inland demo areas")
    counts = {"synthetic_total": 0, "changed": 0, "already_inland": 0, "non_synthetic_untouched": 0}
    with (session_factory or SessionLocal)() as db:
        records = db.scalars(select(Incident).order_by(Incident.id).with_for_update()).all()
        for record in records:
            if record.source_type != "synthetic":
                counts["non_synthetic_untouched"] += 1
                continue
            counts["synthetic_total"] += 1
            if in_demo_land(record.latitude, record.longitude):
                counts["already_inland"] += 1
                continue
            target = targets.get(record.id) or demo_position(record.id, record.police_station)
            print(json.dumps({"mode": "APPLY" if apply else "PREVIEW", "id": record.id,
                              "before": [record.latitude, record.longitude], "after": target}))
            counts["changed"] += 1
            if apply:
                record.latitude, record.longitude = target
        if apply:
            db.flush()
            if any(not in_demo_land(r.latitude, r.longitude) for r in records if r.source_type == "synthetic"):
                raise RuntimeError("Inland validation failed; transaction will roll back")
            db.commit()
        else:
            db.rollback()
    print(json.dumps({"mode": "APPLIED" if apply else "DRY RUN", **counts}))
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    normalize(apply=parser.parse_args().apply)


if __name__ == "__main__":
    main()
