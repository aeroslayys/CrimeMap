"""Fictional operational assets for demonstrating layered command-center maps.

No GPS devices, camera streams, dispatch systems or police databases are connected.
These immutable examples intentionally do not claim to be real Puducherry assets.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi import APIRouter, Depends
from .auth import require_permission

router = APIRouter(prefix="/api/operations", tags=["synthetic-operations"], dependencies=[Depends(require_permission("read"))])

IST = timezone(timedelta(hours=5, minutes=30))
BASE_TIME = datetime(2026, 9, 18, 10, 0, tzinfo=IST)
STEPS = 7
INTERVAL_MINUTES = 10

CAMERAS = [
    {"id": "DEMO-CCTV-01", "label": "Demo camera A", "latitude": 11.9333, "longitude": 79.8295, "zone": "Demo Zone A", "status": "illustrative"},
    {"id": "DEMO-CCTV-02", "label": "Demo camera B", "latitude": 11.9512, "longitude": 79.8185, "zone": "Demo Zone B", "status": "illustrative"},
    {"id": "DEMO-CCTV-03", "label": "Demo camera C", "latitude": 11.9199, "longitude": 79.8044, "zone": "Demo Zone C", "status": "illustrative"},
    {"id": "DEMO-CCTV-04", "label": "Demo camera D", "latitude": 11.9440, "longitude": 79.8238, "zone": "Demo Zone D", "status": "illustrative"},
    {"id": "DEMO-CCTV-05", "label": "Demo camera E", "latitude": 11.9498, "longitude": 79.8182, "zone": "Demo Zone B", "status": "illustrative"},
]

ACCIDENTS = [
    {"id": "DEMO-ACC-01", "label": "Synthetic minor collision", "latitude": 11.9343, "longitude": 79.8298, "severity": "minor", "occurred_at": "2026-09-18T09:20:00+05:30"},
    {"id": "DEMO-ACC-02", "label": "Synthetic road incident", "latitude": 11.9240, "longitude": 79.8144, "severity": "moderate", "occurred_at": "2026-09-18T10:15:00+05:30"},
    {"id": "DEMO-ACC-03", "label": "Synthetic minor collision", "latitude": 11.9490, "longitude": 79.8210, "severity": "minor", "occurred_at": "2026-09-18T08:45:00+05:30"},
    {"id": "DEMO-ACC-04", "label": "Synthetic road incident", "latitude": 11.9313, "longitude": 79.8171, "severity": "moderate", "occurred_at": "2026-09-18T11:00:00+05:30"},
]

# All fixed demo markers/tracks use conservative inland positions near central Puducherry.
# These are illustrative straight-line paths, NOT road routes, verified GPS or a land mask.
PATROL_PATHS = [
    ("DEMO-UNIT-01", "Demo patrol Alpha", "demo_route", [
        (11.9290, 79.8182), (11.9307, 79.8197), (11.9329, 79.8210),
        (11.9340, 79.8227), (11.9353, 79.8240), (11.9360, 79.8255), (11.9372, 79.8263),
    ]),
    ("DEMO-UNIT-02", "Demo patrol Bravo", "demo_route", [
        (11.9500, 79.8190), (11.9479, 79.8196), (11.9460, 79.8204),
        (11.9438, 79.8214), (11.9417, 79.8226), (11.9393, 79.8242), (11.9370, 79.8255),
    ]),
    ("DEMO-UNIT-03", "Demo patrol Charlie", "demo_route", [
        (11.9198, 79.8050), (11.9218, 79.8065), (11.9233, 79.8083),
        (11.9255, 79.8105), (11.9280, 79.8129), (11.9301, 79.8155), (11.9320, 79.8173),
    ]),
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
