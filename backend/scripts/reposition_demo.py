"""Preview or explicitly redistribute original synthetic fixture coordinates only.

This NEVER creates, deletes or reseeds records. It NEVER changes accounts, status,
notes, category, source, or imported/user-created incident records.
Run WITHOUT --apply to inspect proposed changes. Explicit --apply is required.
"""
import argparse
import csv
from pathlib import Path

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Incident

CSV = Path(__file__).resolve().parents[2] / "data" / "synthetic_incidents.csv"
PREVIOUS = Path(__file__).resolve().parents[2] / "data" / "previous_demo_coordinates.csv"

# Snapshot of the original bundled DEMO coordinates, before the inland correction.
# These exact coordinate pairs are used as an optimistic-lock safeguard: if an
# existing record was moved manually, it is skipped, not overwritten.
LEGACY_COORDINATES = {
    "DEMO-0001": (11.933700, 79.829610),
    "DEMO-0002": (11.950400, 79.818550),
    "DEMO-0003": (11.920750, 79.804320),
    "DEMO-0004": (11.944450, 79.822260),
    "DEMO-0005": (11.932450, 79.830030),
    "DEMO-0006": (11.951900, 79.818970),
    "DEMO-0007": (11.919500, 79.804740),
    "DEMO-0008": (11.943200, 79.822680),
    "DEMO-0009": (11.933950, 79.830450),
    "DEMO-0010": (11.950650, 79.819390),
    "DEMO-0011": (11.918250, 79.805160),
    "DEMO-0012": (11.944700, 79.823100),
    "DEMO-0013": (11.932700, 79.828140),
    "DEMO-0014": (11.952150, 79.819810),
    "DEMO-0015": (11.919750, 79.802850),
    "DEMO-0016": (11.943450, 79.823520),
    "DEMO-0017": (11.934200, 79.828560),
    "DEMO-0018": (11.950900, 79.820230),
    "DEMO-0019": (11.918500, 79.803270),
    "DEMO-0020": (11.944950, 79.823940),
    "DEMO-0021": (11.932950, 79.828980),
    "DEMO-0022": (11.949650, 79.820650),
    "DEMO-0023": (11.920000, 79.803690),
    "DEMO-0024": (11.943700, 79.824360),
    "DEMO-0025": (11.934450, 79.829400),
    "DEMO-0026": (11.951150, 79.818340),
    "DEMO-0027": (11.918750, 79.804110),
    "DEMO-0028": (11.945200, 79.822050),
    "DEMO-0029": (11.933200, 79.829820),
    "DEMO-0030": (11.949900, 79.818760),
    "DEMO-0031": (11.920250, 79.804530),
    "DEMO-0032": (11.943950, 79.822470),
    "DEMO-0033": (11.931950, 79.830240),
    "DEMO-0034": (11.951400, 79.819180),
    "DEMO-0035": (11.919000, 79.804950),
    "DEMO-0036": (11.945450, 79.822890),
    "DEMO-0037": (11.933450, 79.830660),
    "DEMO-0038": (11.943450, 79.823100),
    "DEMO-0039": (11.945200, 79.821840),
    "DEMO-0040": (11.950900, 79.819810),
    "DEMO-0041": (11.949900, 79.818550),
    "DEMO-0042": (11.951650, 79.820020),
    "DEMO-0043": (11.943950, 79.822260),
    "DEMO-0044": (11.949650, 79.820230),
    "DEMO-0045": (11.951400, 79.818970),
    "DEMO-0046": (11.943700, 79.823940),
    "DEMO-0047": (11.945450, 79.822680),
    "DEMO-0048": (11.944450, 79.824150),
    "DEMO-0049": (11.950150, 79.819390),
    "DEMO-0050": (11.951900, 79.820860),
    "DEMO-0051": (11.919500, 79.803900),
    "DEMO-0052": (11.949900, 79.818340),
    "DEMO-0053": (11.933950, 79.829610),
    "DEMO-0054": (11.919250, 79.802850),
    "DEMO-0055": (11.931950, 79.829820),
    "DEMO-0056": (11.944700, 79.822260),
    "DEMO-0057": (11.950400, 79.820230),
    "DEMO-0058": (11.934450, 79.828770),
    "DEMO-0059": (11.933450, 79.830240),
    "DEMO-0060": (11.918750, 79.803480),
    "DEMO-0061": (11.920500, 79.804950),
    "DEMO-0062": (11.933200, 79.829190),
    "DEMO-0063": (11.918500, 79.805160),
    "DEMO-0064": (11.944950, 79.823100),
    "DEMO-0065": (11.919250, 79.802640),
    "DEMO-0066": (11.949650, 79.819810),
    "DEMO-0067": (11.951400, 79.818550),
    "DEMO-0068": (11.932700, 79.829820),
    "DEMO-0069": (11.952150, 79.818760),
    "DEMO-0070": (11.951150, 79.820230),
    "DEMO-0071": (11.950150, 79.818970),
    "DEMO-0072": (11.951900, 79.820440),
    "DEMO-0073": (11.933200, 79.828980),
    "DEMO-0074": (11.949900, 79.820650),
    "DEMO-0075": (11.951650, 79.819390),
    "DEMO-0076": (11.932950, 79.830660),
    "DEMO-0077": (11.949650, 79.819600),
    "DEMO-0078": (11.933700, 79.828140),
    "DEMO-0079": (11.943700, 79.823310),
    "DEMO-0080": (11.920750, 79.802850),
    "DEMO-0081": (11.919750, 79.804320),
    "DEMO-0082": (11.918750, 79.803060),
    "DEMO-0083": (11.920500, 79.804530),
    "DEMO-0084": (11.933200, 79.828770),
    "DEMO-0085": (11.943200, 79.823940),
    "DEMO-0086": (11.920250, 79.803480),
    "DEMO-0087": (11.919250, 79.804950),
    "DEMO-0088": (11.942950, 79.822890),
    "DEMO-0089": (11.951400, 79.820860),
    "DEMO-0090": (11.943700, 79.823100),
    "DEMO-0091": (11.945450, 79.821840),
    "DEMO-0092": (11.951150, 79.819810),
    "DEMO-0093": (11.932450, 79.828350),
    "DEMO-0094": (11.920500, 79.804320),
    "DEMO-0095": (11.944200, 79.822260),
    "DEMO-0096": (11.949900, 79.820230),
    "DEMO-0097": (11.933950, 79.828770),
    "DEMO-0098": (11.943950, 79.823940),
    "DEMO-0099": (11.949650, 79.819180),
    "DEMO-0100": (11.920000, 79.804950),
}


def same_point(actual, expected):
    return all(abs(a - b) <= 0.0000005 for a, b in zip(actual, expected))



def redistribution_plan(db, *, apply=False):
    """Count or move ONLY unchanged canonical synthetic DEMO coordinates.

    A server route may call this with its current session. No implicit commit
    occurs, so the caller can add a single audit event in the same transaction.
    User-created and imported UUID records are never candidates.
    """
    with PREVIOUS.open(encoding="utf-8", newline="") as source:
        previous = {
            row["id"]: (float(row["old_latitude"]), float(row["old_longitude"]))
            for row in csv.DictReader(source)
        }
    with CSV.open(encoding="utf-8", newline="") as source:
        targets = {
            row["id"]: (float(row["latitude"]), float(row["longitude"]))
            for row in csv.DictReader(source)
        }
    query = select(Incident).where(Incident.id.in_(list(targets)))
    if apply:
        query = query.with_for_update()
    records = {record.id: record for record in db.scalars(query)}
    result = {
        "canonical_total": len(targets),
        "ready_to_move": 0,
        "already_current": 0,
        "skipped_custom": 0,
        "missing": 0,
        "updated": 0,
    }
    for identifier, target in targets.items():
        record = records.get(identifier)
        if record is None:
            result["missing"] += 1
            continue
        if record.source_type != "synthetic":
            result["skipped_custom"] += 1
            continue
        current = (float(record.latitude), float(record.longitude))
        if same_point(current, target):
            result["already_current"] += 1
        elif any(known is not None and same_point(current, known)
                 for known in (previous.get(identifier), LEGACY_COORDINATES.get(identifier))):
            result["ready_to_move"] += 1
            if apply:
                record.latitude, record.longitude = target
                result["updated"] += 1
        else:
            result["skipped_custom"] += 1
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Commit moves of untouched canonical demo pins (default: preview)")
    args = parser.parse_args(argv)
    with SessionLocal() as db:
        result = redistribution_plan(db, apply=args.apply)
        if args.apply:
            db.commit()
        else:
            db.rollback()
    print(f"{'Applied' if args.apply else 'Preview'} canonical demo redistribution: {result}")
    if not args.apply:
        print("Dry run only. No database rows changed. Use --apply after reviewing the preview.")


if __name__ == "__main__":
    main()
