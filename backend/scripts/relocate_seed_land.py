"""Explicit, conservative relocation of ORIGINAL demo fixture coordinates only.

This is never run at app startup, on seeding, or on a code deployment.
Default is read-only --dry-run. --apply requires explicit acknowledgement.
It cannot update arbitrary incidents, manual imports, user accounts or plans.
"""
import argparse
import csv
from datetime import datetime, timezone
from math import isclose
from pathlib import Path

from app.db import SessionLocal
from app.models import Incident

MANIFEST = Path(__file__).resolve().parents[2] / "data" / "seed_land_coordinate_migration.csv"
ACKNOWLEDGEMENT = "I-understand-only-canonical-synthetic-coordinates-change"


def same_coordinate(actual: float, expected: float) -> bool:
    return isclose(actual, expected, rel_tol=0, abs_tol=1e-8)


def relocation_summary(*, apply: bool = False, session_factory=None, manifest: Path = MANIFEST) -> dict:
    """Compare against the *original* CSV fingerprint, then touch only latitude/longitude."""
    session_factory = session_factory or SessionLocal
    counts = {"matched": 0, "already_corrected": 0, "missing": 0, "modified_or_unrecognized": 0}
    with session_factory() as db, manifest.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            rec = db.get(Incident, row["id"])
            if rec is None:
                counts["missing"] += 1
                continue
            expected_utc = datetime.fromisoformat(row["occurred_at"]).astimezone(timezone.utc)
            original = (
                rec.id == row["id"]
                and rec.source_type == "synthetic"
                and rec.category == row["category"]
                and rec.occurred_at == expected_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                and rec.police_station == row["police_station"]
                and rec.description == row["description"]
            )
            if not original:
                counts["modified_or_unrecognized"] += 1
                continue
            old_lat, old_lon = float(row["old_latitude"]), float(row["old_longitude"])
            new_lat, new_lon = float(row["new_latitude"]), float(row["new_longitude"])
            if same_coordinate(rec.latitude, new_lat) and same_coordinate(rec.longitude, new_lon):
                counts["already_corrected"] += 1
            elif same_coordinate(rec.latitude, old_lat) and same_coordinate(rec.longitude, old_lon):
                counts["matched"] += 1
                if apply:
                    rec.latitude, rec.longitude = new_lat, new_lon
            else:
                counts["modified_or_unrecognized"] += 1
        if apply:
            db.commit()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview or explicitly relocate ORIGINAL fictional DEMO fixture coordinates inland"
    )
    parser.add_argument("--apply", action="store_true", help="Commit matching seed coordinate changes")
    parser.add_argument("--acknowledge", default="", help="Required explicit confirmation for --apply")
    options = parser.parse_args()
    if options.apply and options.acknowledge != ACKNOWLEDGEMENT:
        parser.error("--apply requires --acknowledge " + ACKNOWLEDGEMENT)
    counts = relocation_summary(apply=options.apply)
    print(("APPLIED" if options.apply else "DRY RUN / NO DATA CHANGED"), counts)
    if counts["modified_or_unrecognized"]:
        print("Existing edited/unrecognized incidents were left untouched; inspect separately.")


if __name__ == "__main__":
    main()
