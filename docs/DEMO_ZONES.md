# Distributed demo incidents and visible sectors

CrimeMap's canonical 100 `DEMO-0001`–`DEMO-0100` records are **fictional**.
They are now distributed near multiple Puducherry neighborhoods, rather than
being confined to four compact blocks. They represent neither verified crime
locations nor police-station coverage.

## What the four illustrated sectors mean

| Sector | Direction | Descriptive coverage | Approximate coordinates |
| --- | --- | --- | --- |
| Zone A | North and northeast | Muthialpet/Lawspet through Kuilapalayam to Kalapet | 11.945–12.037° N, 79.810–79.869° E |
| Zone B | Central/eastern city | Nellithoppe/Orleanpet to Grand Bazaar/town center | 11.925–11.945° N, 79.809–79.846° E |
| Zone C | South/southeast | Mudaliarpet via Murungapakkam and Ariyankuppam to Nallavadu | 11.847–11.925° N, 79.797–79.845° E |
| Zone D | West/southwest | Mettupalayam/Reddiarpalayam via Villianur to Mangalam/Karikalampakkam | 11.847–11.952° N, 79.731–79.809° E |

Zone C and Zone D are **irregular demonstration polygons**, not bounding
rectangles. Exact polygon vertices and the coordinate-based point-in-zone
check live in `frontend/src/modules/map/demo-zones.js`. The reference
neighborhoods are derived from published
[Puducherry Police location coordinates](https://police.py.gov.in/lat_log_police%20unit.php)
and locality references, but **the drawn zone boundaries are not published by
the police**. They are neither cadastral polygons nor a verified land/water mask.

## How to view zones

After logging in, go to **Geospatial Intelligence → Zones**.
Distinct outlines are shown on the existing OpenStreetMap canvas. Click a
polygon or **View this zone** to zoom into it and show only incident points
**inside that polygon**. Choose **Show all zones** to view all four again.
Each card gives a “from → to” neighborhood description and approximate
latitude/longitude extent. The regular marker, heatmap, grid and simulated
operations modes remain available.

New incident pins suggest a zone using the same geometry. Editable
`police_station` values remain editable labels; geographic selection in
**Zones mode** deliberately uses coordinates, not these labels.
Existing analytics and Grid Analysis `zone` filters still use the stored
label and are separate from the boundary selection.

## Database safety: existing installs must opt in

Updating the CSV and code **does not move previously seeded database rows**.
`scripts.seed_demo` is insert-only. To review canonical synthetic pins only,
run in your configured environment:

```bash
cd backend
python -m scripts.reposition_demo
```

Only if the reported changes are expected **and you have a backup**, run:

```bash
python -m scripts.reposition_demo --apply
```

This one-time script recognizes either the original fixture location or the
immediately preceding four-block snapshot in
`data/previous_demo_coordinates.csv`. It changes **only latitude and
longitude**, and only for matching canonical `DEMO-` IDs marked
`source_type=synthetic`. It skips missing IDs, independently moved pins,
and imported/user-created records. It does not reset users, statuses, notes,
or other fields. Both forms use the *database configured for that execution*,
so local SQLite and deployed Cloud SQL require separate explicit operations.
For a Cloud SQL dry-run, use a standalone review Cloud Run Job with the
current image and DB configuration; do not rerun `crimemap-init`.

The revised canonical points are distributed near urban reference locations,
with small deterministic offsets. **They have not been snapped to streets
or exhaustively checked against GIS water polygons.** Visually verify the
basemap for demonstrations. This is illustrative data only.
