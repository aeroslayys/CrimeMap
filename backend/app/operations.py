"""Fictional operational assets for demonstrating layered command-center maps.

No GPS devices, camera streams, dispatch systems or police databases are connected.
These immutable examples intentionally do not claim to be real Puducherry assets.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from .auth import require_permission
from .demo_land import demo_position

router = APIRouter(prefix="/api/operations", tags=["synthetic-operations"], dependencies=[Depends(require_permission("read"))])

IST = timezone(timedelta(hours=5, minutes=30))
BASE_TIME = datetime(2026, 9, 18, 10, 0, tzinfo=IST)
STEPS = 7
INTERVAL_MINUTES = 10

CAMERAS = [
    {"id": "DEMO-CCTV-01", "label": "Demo camera A", "zone": "Demo Zone A", "status": "illustrative"},
    {"id": "DEMO-CCTV-02", "label": "Demo camera B", "zone": "Demo Zone B", "status": "illustrative"},
    {"id": "DEMO-CCTV-03", "label": "Demo camera C", "zone": "Demo Zone C", "status": "illustrative"},
    {"id": "DEMO-CCTV-04", "label": "Demo camera D", "zone": "Demo Zone D", "status": "illustrative"},
    {"id": "DEMO-CCTV-05", "label": "Demo camera E", "zone": "Demo Zone B", "status": "illustrative"},
]

ACCIDENTS = [
    {"id": "DEMO-ACC-01", "label": "Synthetic minor collision", "severity": "minor", "occurred_at": "2026-09-18T09:20:00+05:30"},
    {"id": "DEMO-ACC-02", "label": "Synthetic road incident", "severity": "moderate", "occurred_at": "2026-09-18T10:15:00+05:30"},
    {"id": "DEMO-ACC-03", "label": "Synthetic minor collision", "severity": "minor", "occurred_at": "2026-09-18T08:45:00+05:30"},
    {"id": "DEMO-ACC-04", "label": "Synthetic road incident", "severity": "moderate", "occurred_at": "2026-09-18T11:00:00+05:30"},
]

# These are fictional reference-area points, NOT device locations or GPS feeds.
# Individual patrol routes must remain near ONE neighborhood anchor: repeated
# demo_position calls with different IDs would jump across distant neighborhoods.
for camera in CAMERAS:
    camera["latitude"], camera["longitude"] = demo_position(camera["id"], camera["zone"])
for index, accident in enumerate(ACCIDENTS):
    accident["latitude"], accident["longitude"] = demo_position(accident["id"], f"Demo Zone {chr(65 + index)}")

def local_demo_track(index, zone):
    """Seven close-by fictional positions; never interpolate across neighborhoods."""
    lat, lon = demo_position(f"patrol-{index}", zone)
    return [
        (round(lat + (step - 3) * 0.00005, 6),
         round(lon + (step - 3) * 0.00005, 6))
        for step in range(STEPS)
    ]


PATROL_PATHS = [
    (f"DEMO-UNIT-{index:02d}", f"Demo patrol {label}", "demo_route",
     local_demo_track(index, zone))
    for index, label, zone in [(1, "Alpha", "Demo Zone A"),
                               (2, "Bravo", "Demo Zone B"),
                               (3, "Charlie", "Demo Zone C")]
]


def make_patrol(unit_id, label, status, locations):
    return {
        "id": unit_id,
        "label": label,
        "status": status,
        "source_type": "synthetic",
        "track": [
            {
                "timestamp": (BASE_TIME + timedelta(minutes=i * INTERVAL_MINUTES)).isoformat(),
                "latitude": lat,
                "longitude": lon,
            }
            for i, (lat, lon) in enumerate(locations)
        ],
    }


@router.get("/overview")
def overview():
    """Read-only synthetic overlays with timestamped *historical demo* tracks."""
    return {
        "source_type": "synthetic",
        "data_label": "SYNTHETIC DEMONSTRATION DATA",
        "simulation": True,
        "live_tracking": False,
        "timezone": "Asia/Kolkata",
        "description": "Fictional patrol routes, hypothetical CCTV assets and accident records. No live feeds or actual police assets.",
        "timeline": {
            "start": BASE_TIME.isoformat(),
            "interval_minutes": INTERVAL_MINUTES,
            "steps": STEPS,
        },
        "cameras": [{**camera, "source_type": "synthetic"} for camera in CAMERAS],
        "accidents": [{**accident, "source_type": "synthetic"} for accident in ACCIDENTS],
        "patrols": [make_patrol(*unit) for unit in PATROL_PATHS],
    }
