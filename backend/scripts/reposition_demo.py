"""Preview or explicitly update unchanged legacy synthetic fixture coordinates only.

This NEVER creates, deletes or reseeds records. It NEVER changes accounts, status,
notes, category, source, or imported/user-created incident records.
Run WITHOUT --apply to inspect proposed changes. Explicit --apply is required.
"""
import argparse
import csv
from pathlib import Path

from app.db import SessionLocal
from app.models import Incident

CSV = Path(__file__).resolve().parents[2] / "data" / "synthetic_incidents.csv"

# Snapshot of the original bundled DEMO coordinates, before the inland correction.
# These exact coordinate pairs are used as an optimistic-lock safeguard: if an
# existing record was moved manually, it is skipped, not overwritten.
LEGACY_COORDINATES = {
    "DEMO-0001": (11.931662, 79.833761),
    "DEMO-0002": (11.952461, 79.817384),
    "DEMO-0003": (11.92243, 79.805319),
    "DEMO-0004": (11.942054, 79.844718),
    "DEMO-0005": (11.930934, 79.830035),
    "DEMO-0006": (11.949944, 79.819631),
    "DEMO-0007": (11.917946, 79.80562),
    "DEMO-0008": (11.946793, 79.842074),
    "DEMO-0009": (11.934167, 79.83195),
    "DEMO-0010": (11.952349, 79.817186),
    "DEMO-0011": (11.919352, 79.804316),
    "DEMO-0012": (11.942424, 79.844839),
    "DEMO-0013": (11.933216, 79.828789),
    "DEMO-0014": (11.950897, 79.818587),
    "DEMO-0015": (11.918336, 79.802466),
    "DEMO-0016": (11.944564, 79.839422),
    "DEMO-0017": (11.932778, 79.83129),
    "DEMO-0018": (11.948162, 79.821351),
    "DEMO-0019": (11.917443, 79.802532),
    "DEMO-0020": (11.946703, 79.840325),
    "DEMO-0021": (11.931945, 79.831557),
    "DEMO-0022": (11.950013, 79.819065),
    "DEMO-0023": (11.920228, 79.804396),
    "DEMO-0024": (11.942146, 79.843898),
    "DEMO-0025": (11.931097, 79.828486),
    "DEMO-0026": (11.94985, 79.820987),
    "DEMO-0027": (11.920973, 79.804243),
    "DEMO-0028": (11.944668, 79.840318),
    "DEMO-0029": (11.933108, 79.830303),
    "DEMO-0030": (11.947785, 79.816881),
    "DEMO-0031": (11.917756, 79.805607),
    "DEMO-0032": (11.947093, 79.843533),
    "DEMO-0033": (11.930717, 79.829083),
    "DEMO-0034": (11.953103, 79.818344),
    "DEMO-0035": (11.918203, 79.804929),
    "DEMO-0036": (11.945512, 79.842244),
    "DEMO-0037": (11.928167, 79.834819),
    "DEMO-0038": (11.935104, 79.838248),
    "DEMO-0039": (11.940055, 79.838313),
    "DEMO-0040": (11.945934, 79.821652),
    "DEMO-0041": (11.946525, 79.816761),
    "DEMO-0042": (11.931760, 79.827043),
    "DEMO-0043": (11.943587, 79.845722),
    "DEMO-0044": (11.950291, 79.822816),
    "DEMO-0045": (11.949676, 79.816458),
    "DEMO-0046": (11.941096, 79.845810),
    "DEMO-0047": (11.947880, 79.844661),
    "DEMO-0048": (11.940428, 79.842709),
    "DEMO-0049": (11.954801, 79.821228),
    "DEMO-0050": (11.949355, 79.814128),
    "DEMO-0051": (11.913638, 79.803285),
    "DEMO-0052": (11.951149, 79.822454),
    "DEMO-0053": (11.932986, 79.827074),
    "DEMO-0054": (11.918304, 79.800211),
    "DEMO-0055": (11.932052, 79.834438),
    "DEMO-0056": (11.948103, 79.842852),
    "DEMO-0057": (11.955869, 79.821807),
    "DEMO-0058": (11.933245, 79.831781),
    "DEMO-0059": (11.930447, 79.832203),
    "DEMO-0060": (11.919493, 79.800100),
    "DEMO-0061": (11.917685, 79.800700),
    "DEMO-0062": (11.932110, 79.830482),
    "DEMO-0063": (11.919774, 79.803100),
    "DEMO-0064": (11.949593, 79.836745),
    "DEMO-0065": (11.923548, 79.800100),
    "DEMO-0066": (11.953466, 79.823903),
    "DEMO-0067": (11.950021, 79.819535),
    "DEMO-0068": (11.930237, 79.834095),
    "DEMO-0069": (11.949609, 79.818101),
    "DEMO-0070": (11.952795, 79.824944),
    "DEMO-0071": (11.961522, 79.849080),
    "DEMO-0072": (11.956157, 79.821275),
    "DEMO-0073": (11.933788, 79.824564),
    "DEMO-0074": (11.956704, 79.824499),
    "DEMO-0075": (11.950459, 79.815321),
    "DEMO-0076": (11.927310, 79.827449),
    "DEMO-0077": (11.926114, 79.844342),
    "DEMO-0078": (11.933336, 79.828268),
    "DEMO-0079": (11.949160, 79.843524),
    "DEMO-0080": (11.918352, 79.808418),
    "DEMO-0081": (11.916418, 79.827749),
    "DEMO-0082": (11.925408, 79.809426),
    "DEMO-0083": (11.919170, 79.800419),
    "DEMO-0084": (11.936410, 79.828323),
    "DEMO-0085": (11.946099, 79.829157),
    "DEMO-0086": (11.922264, 79.801649),
    "DEMO-0087": (11.924867, 79.803495),
    "DEMO-0088": (11.943494, 79.839277),
    "DEMO-0089": (11.951749, 79.817889),
    "DEMO-0090": (11.923482, 79.811260),
    "DEMO-0091": (11.949407, 79.837138),
    "DEMO-0092": (11.950720, 79.824108),
    "DEMO-0093": (11.927938, 79.827407),
    "DEMO-0094": (11.919575, 79.808241),
    "DEMO-0095": (11.958854, 79.809871),
    "DEMO-0096": (11.948469, 79.819072),
    "DEMO-0097": (11.915195, 79.803037),
    "DEMO-0098": (11.939039, 79.836762),
    "DEMO-0099": (11.948836, 79.814792),
    "DEMO-0100": (11.918995, 79.804560),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Update only matching unchanged legacy demo coordinates")
    args = parser.parse_args(argv)
    proposed = 0
    skipped = 0
    unchanged = 0
    with SessionLocal() as db, CSV.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            identifier = row["id"]
            original = LEGACY_COORDINATES.get(identifier)
            if original is None:
                raise RuntimeError(f"Unknown canonical ID: {identifier}")
            record = db.get(Incident, identifier)
            if record is None or record.source_type != "synthetic":
                skipped += 1
                continue
            target = (float(row["latitude"]), float(row["longitude"]))
            current = (float(record.latitude), float(record.longitude))
            if current == target:
                unchanged += 1
                continue
            if any(abs(a - b) > 0.0000005 for a, b in zip(current, original)):
                print(f"SKIP {identifier}: coordinates were manually changed ({current})")
                skipped += 1
                continue
            proposed += 1
            print(f"{'APPLY' if args.apply else 'PREVIEW'} {identifier}: {current} -> {target}")
            if args.apply:
                record.latitude, record.longitude = target
        if args.apply:
            db.commit()
        else:
            db.rollback()
    print(f"{'Updated' if args.apply else 'Would update'} {proposed} legacy fixtures; "
          f"{unchanged} already corrected; {skipped} missing, non-demo or custom-positioned.")
    if not args.apply:
        print("No database records were changed. Use --apply only after reviewing the preview.")


if __name__ == "__main__":
    main()
