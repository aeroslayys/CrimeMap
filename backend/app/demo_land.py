"""Conservative urban reference envelopes for geographically spread *fictional* data.

These are not official police jurisdictions or a full land/water GIS layer.
Legacy inland rectangles remain accepted for older demo operational assets.
"""
from hashlib import sha256
from math import isfinite

# Anchors from published Puducherry Police coordinates and OSM locality references.
ZONE_SITES = {
    "Demo Zone A": [
        (12.031256, 79.863972),  # Kalapet
        (11.989453, 79.832826),  # Kuilapalayam
        (11.957636, 79.822505),  # Lawspet
        (11.957844, 79.814558),  # Lawspet West
        (11.947456, 79.831503),  # Muthialpet
        (11.950722, 79.836403),  # Solai Nagar
        (11.959508, 79.834835),  # Kottakuppam
    ],
    "Demo Zone B": [
        (11.936242, 79.827969),  # Grand Bazaar
        (11.931167, 79.817878),  # Orleanpet
        (11.930044, 79.824025),  # Odiansalai
        (11.929314, 79.815667),  # Nellithoppe
        (11.935100, 79.816167),  # Iyyanar Koil
        (11.937900, 79.821340),  # Town Center
    ],
    "Demo Zone C": [
        (11.921544, 79.815575),  # Mudaliarpet
        (11.915505, 79.807075),  # Southern Mudaliarpet
        (11.905124, 79.808662),  # Murungapakkam
        (11.894870, 79.807590),  # Ariyankuppam
        (11.854554, 79.811464),  # Nallavadu
    ],
    "Demo Zone D": [
        (11.939956, 79.790133),  # Mettupalayam
        (11.949776, 79.797454),  # Dhanvantry Nagar
        (11.930856, 79.806100),  # Reddiarpalayam
        (11.912719, 79.755164),  # Villianur
        (11.892667, 79.739344),  # Mangalam
        (11.860930, 79.749661),  # Karikalampakkam
        (11.861614, 79.782168),  # Abishegapakkam
    ],
}
LEGACY_INLAND_AREAS = (
    (11.9320, 11.9334, 79.8103, 79.8117),
    (11.9566, 11.9580, 79.8220, 79.8234),
    (11.9214, 11.9228, 79.8153, 79.8167),
    (11.9301, 11.9315, 79.8055, 79.8069),
)
SITE_MARGIN = 0.0015


def in_demo_land(latitude, longitude):
    """Reference-area check for fixtures, NOT a complete land/water validator."""
    if not (isfinite(latitude) and isfinite(longitude)):
        return False
    return (
        any(s <= latitude <= n and w <= longitude <= e
            for s, n, w, e in LEGACY_INLAND_AREAS)
        or any(abs(latitude - lat) <= SITE_MARGIN and
               abs(longitude - lon) <= SITE_MARGIN
               for sites in ZONE_SITES.values() for lat, lon in sites)
    )


def demo_position(identifier, zone=None):
    """Return a reproducible fictional coordinate near one distributed reference."""
    digest = sha256(identifier.encode()).digest()
    names = tuple(ZONE_SITES)
    name = zone if zone in ZONE_SITES else names[digest[0] % len(names)]
    sites = ZONE_SITES[name]
    latitude, longitude = sites[digest[1] % len(sites)]
    lat_offset = (int.from_bytes(digest[2:6], "big") / (2**32 - 1) - 0.5) * 0.0022
    lon_offset = (int.from_bytes(digest[6:10], "big") / (2**32 - 1) - 0.5) * 0.0022
    return round(latitude + lat_offset, 6), round(longitude + lon_offset, 6)
