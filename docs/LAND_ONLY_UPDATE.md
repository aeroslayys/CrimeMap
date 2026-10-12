# Inland synthetic-data update — existing Cloud Run deployment

The bundled 100 incidents already use four small inland Puducherry demo areas.
This update also places all camera/accident fixtures and every patrol segment
inside those areas. `scripts.normalize_synthetic_land` corrects **every existing
synthetic incident outside those areas**, including imported UUIDs and edited
DEMO records that the older migrations deliberately skipped.

This is demo normalization, not geographic water detection: even valid land
locations outside the four areas move. The coordinates are fictional; the areas
are not police jurisdiction boundaries. Arbitrary future manual entries/imports
are not geofenced. Run the correction again if more old data is imported.

Only latitude and longitude change. IDs, counts, notes, categories, dates,
statuses, user accounts and prevention plans are preserved. Non-synthetic records
are excluded and counted explicitly. Existing prevention-plan geometry remains
unchanged; review plans based on the old locations separately.

## 1. Pull, build and deploy

Run in Cloud Shell from your existing `aeroslayys/CrimeMap` checkout. Resolve any
local uncommitted changes before pulling; do not discard them.

```bash
cd ~/CrimeMap
git status
git switch dev/shwetha
git pull --ff-only origin dev/shwetha

export PROJECT_ID="crimemap-511218"
export REGION="asia-south1"
gcloud config set project "$PROJECT_ID"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/crimemap/crimemap:$(git rev-parse --short HEAD)"

gcloud builds submit --region="$REGION" --tag="$IMAGE" .
gcloud run deploy crimemap --image="$IMAGE" --region="$REGION"
```

Stop if any command fails. Run the next sections in the same Cloud Shell session
so the variables remain available. The existing service retains its database and
secret configuration. Do not execute `crimemap-init` or reset/reseed the database.

## 2. Configure a separate correction job and preview

These are the existing deployment's documented instance, account and secret names.
The job explicitly enables Cloud SQL mode so it cannot silently use SQLite.
`jobs deploy` creates or updates this dedicated job and resets its default args
to preview mode each time.

```bash
export CONNECTION="$(gcloud sql instances describe crimemap-db --format='value(connectionName)')"
export SERVICE_ACCOUNT="crimemap-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run jobs deploy crimemap-land-fix \
  --image="$IMAGE" --region="$REGION" \
  --service-account="$SERVICE_ACCOUNT" \
  --set-cloudsql-instances="$CONNECTION" \
  --set-env-vars="CRIMEMAP_DEPLOYMENT=cloud-run,CLOUD_SQL_CONNECTION_NAME=$CONNECTION,DB_NAME=crimemap,DB_USER=crimemap_app" \
  --set-secrets="DB_PASS=crimemap-db-password:latest" \
  --command=python --args=-m,scripts.normalize_synthetic_land \
  --tasks=1 --parallelism=1 --max-retries=0

gcloud run jobs execute crimemap-land-fix --region="$REGION" --wait

gcloud logging read 'resource.type="cloud_run_job" AND resource.labels.job_name="crimemap-land-fix"' \
  --freshness=1h --limit=1000 --order=asc --format='json(timestamp,textPayload,jsonPayload)'
```

Preview ends with `"mode": "DRY RUN"`, the total synthetic count and `changed`
(number of proposed moves). Each proposed move logs its ID and before/after
coordinates. No data changes in preview. Check logs for the latest execution if
you have run it more than once.

## 3. Apply, then verify

Avoid adding/editing incidents during this short correction. It commits all
coordinate updates together and validates the resulting synthetic coordinates
before committing. Retain the job's before/after logs for coordinate recovery.

```bash
gcloud run jobs execute crimemap-land-fix --region="$REGION" \
  --args=-m,scripts.normalize_synthetic_land,--apply --wait

# Default job args are still preview-only; verify nothing remains to move.
gcloud run jobs execute crimemap-land-fix --region="$REGION" --wait

gcloud logging read 'resource.type="cloud_run_job" AND resource.labels.job_name="crimemap-land-fix"' \
  --freshness=1h --limit=1000 --order=asc --format='json(timestamp,textPayload,jsonPayload)'
```

The apply execution must succeed with `"mode": "APPLIED"`. The subsequent
preview must show `"changed": 0` and `already_inland == synthetic_total`.
If `non_synthetic_untouched` is nonzero, those rows were deliberately excluded;
this result does not certify them as inland.

Refresh the website and check Markers, Heatmap and Operations. Heatmap blur and
square analytical grid cells are rendering geometry, not extra incident locations;
at very low zoom they can extend beyond the underlying points. No coastline
clipping is added by this update.

Local SQLite equivalent, from `backend/` with your existing environment:

```bash
python -m scripts.normalize_synthetic_land
python -m scripts.normalize_synthetic_land --apply
python -m scripts.normalize_synthetic_land
```

## Geographic verification

The four small areas were visually checked against OpenStreetMap street/water
mapping on 12 October 2026; all are inland urban blocks. Automated checks cover
both 100-row CSVs, operational points, patrol segment interpolation, and migration
idempotence/metadata preservation. These checks are deliberately scoped to this
fictional dataset rather than claiming a general coastline classifier.

Map references (OpenStreetMap contributors, https://www.openstreetmap.org/copyright):
- Zone A: https://www.openstreetmap.org/?mlat=11.9327&mlon=79.8110#map=18/11.9327/79.8110
- Zone B: https://www.openstreetmap.org/?mlat=11.9573&mlon=79.8227#map=18/11.9573/79.8227
- Zone C: https://www.openstreetmap.org/?mlat=11.9221&mlon=79.8160#map=18/11.9221/79.8160
- Zone D: https://www.openstreetmap.org/?mlat=11.9308&mlon=79.8062#map=18/11.9308/79.8062

References:
- https://docs.cloud.google.com/sdk/gcloud/reference/run/jobs/deploy
- https://docs.cloud.google.com/sdk/gcloud/reference/run/jobs/execute
