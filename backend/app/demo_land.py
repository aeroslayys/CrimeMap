"""Small inland demo areas, not a general-purpose coastline or jurisdiction map.

Only these four urban blocks are used for fictional fixtures. Outside does not
mean water: normalization intentionally trades geographic spread for inland demos.
"""
from hashlib import sha256
from math import isfinite

INLAND_AREAS = {
    "Demo Zone A": (11.9320, 11.9334, 79.8103, 79.8117),
    "Demo Zone B": (11.9566, 11.9580, 79.8220, 79.8234),
    "Demo Zone C": (11.9214, 11.9228, 79.8153, 79.8167),
    "Demo Zone D": (11.9301, 11.9315, 79.8055, 79.8069),
}


def in_demo_land(latitude, longitude):
    return isfinite(latitude) and isfinite(longitude) and any(
        south <= latitude <= north and west <= longitude <= east
        for south, north, west, east in INLAND_AREAS.values()
    )


def demo_position(identifier, zone=None):
    """Stable fictional position with a margin inside a selected inland block."""
    digest = sha256(identifier.encode()).digest()
    zone = zone if zone in INLAND_AREAS else tuple(INLAND_AREAS)[digest[0] % 4]
    south, north, west, east = INLAND_AREAS[zone]
    lat_fraction = 0.15 + 0.7 * int.from_bytes(digest[1:5], "big") / (2**32 - 1)
    lon_fraction = 0.15 + 0.7 * int.from_bytes(digest[5:9], "big") / (2**32 - 1)
    return round(south + (north - south) * lat_fraction, 6), round(west + (east - west) * lon_fraction, 6)
