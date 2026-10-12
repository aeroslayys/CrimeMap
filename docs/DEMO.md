# CrimeMap — 5-minute Cloud Run hackathon demo

**Primary demo: [CrimeMap on Google Cloud Run](https://crimemap-595311113823.asia-south1.run.app)** · Project `crimemap-511218` · Region `asia-south1` (Mumbai) · Source branch `dev/shwetha`

> **Synthetic demonstration data only.** Every incident, zone, map finding, operational overlay, statistic and prevention suggestion is fictional. CrimeMap is a hackathon proof of concept, **not** a verified Puducherry Police system, real crime forecast or operational policing tool.

This presentation runs from the **deployed HTTPS application**, not a local Vite/FastAPI development server. The React frontend and FastAPI API share a Cloud Run service; persistent users, fictional incidents and plans live in a separate **Cloud SQL PostgreSQL** database. The presenter only needs a browser, working internet, and an existing CrimeMap account with the right permissions.

## Before presenting — cloud checklist

- **Confirm access ahead of time.** Open [the deployed site](https://crimemap-595311113823.asia-south1.run.app) in the **same browser and network** you will use on stage. The Cloud Run service was originally deployed with an IAM invoker check. If you get **403 before the login screen**, ask the deployment administrator to verify Cloud Run's authentication/invoker setting: browser access requires either an authorized Google Cloud identity or a consciously enabled publicly reachable *synthetic-only* demo. Do not change exposure settings during the talk.
- **Prepare an app login.** Use a separate **Officer or Administrator** CrimeMap account already created in the cloud database. Administrator is needed to demonstrate **User management / audit history**; Officer is sufficient for incident and plan changes. The initial cloud admin username was `demo-admin`, but **never display or share its password**. Local SQLite usernames/passwords do not automatically work on Cloud Run.
- **Check readiness.** Sign in, load **Incidents**, **Geospatial Intelligence**, **Analytics** and **Prevention planner**. Verify that fictional incident counts reflect the **current cloud database**, rather than assuming exactly 100: 100 seed fixtures were inserted during first-time initialization, and teammates may have added more.
- **Use projector-friendly light mode.** CrimeMap defaults to its high-contrast light palette, with a **Light mode / Dark mode** toggle on sign-in and in the workspace header. Choose light mode in advance, use about **100–110% browser zoom** if it fits the screen, and check legibility on the **actual projector**. Theme choice is saved in the browser, not the database.
- **Prepare the prevention segment.** Ideally have an existing **completed fictional plan** available so you can demonstrate **Review observed counts**. Otherwise show a proposal and explain the workflow; do not manufacture or alter results for the presentation. Open **How these suggestions are generated** (the visible methodology card) to explain limits.
- **Prepare report and fallback.** Build and save a **synthetic presentation PDF** from Analytics before the session; also save a few screenshots of the map/analytics and, optionally, a short screen recording. Verify OpenStreetMap tiles display over the venue connection. Avoid showing the Google Cloud Console, credentials, API tokens or other private browser tabs on the projector.
- **Do not run first-time setup again.** Do **not** rerun `crimemap-init`, recreate Cloud SQL, reset accounts, reseed the database, or import real incident records. GitHub code updates **do not automatically deploy** to Cloud Run; verify the intended revision is live *before* the event. The Cloud SQL trial or billing state may affect availability.

**Optional health check** (only when the Cloud Run endpoint is configured to accept unauthenticated requests):

```bash
curl -i https://crimemap-595311113823.asia-south1.run.app/health
```

A reachable, healthy app should respond with HTTP `200` and `{"status":"ok"}`. A `403` means Cloud Run access control may be blocking the request, **not** that the database was wiped. If the service is private, an administrator can verify it using authorized Google Cloud tools; see [Cloud deployment handoff](CLOUD_DEPLOYMENT.md).

## Live walkthrough — 5 minutes

| Time | Workspace | What to demonstrate and say |
| --- | --- | --- |
| **0:00–0:30** | **Incidents** | “This is the live cloud-deployed demo, backed by PostgreSQL. All records are fictional.” Show the current incident count, filtering and search. Highlight that cloud records persist between logins/redeployments. |
| **0:30–1:10** | **Add incident** | Open the form; click/drag the map pin to capture coordinates and suggest a nearby **fictional** demonstration zone. **Cancel** instead of saving unless a prepared synthetic test record is needed. |
| **1:10–2:00** | **Geospatial intelligence** | Click **Map** on a registry record to locate it, then show **Markers**, **Heatmap** or **Grid analysis → Compare periods**. Point out the descriptive counts, fixed geographic grid and non-predictive interpretation. Operations overlays are simulated, not live patrol/CCTV feeds. |
| **2:00–2:50** | **Analytics** | Show category, status, date/hour and demonstration-zone summaries. Apply/clear a filter; explain that aggregates cover **all matching records in Cloud SQL**, not just the current registry page. |
| **2:50–4:00** | **Prevention planner** | Show category-specific safeguarding suggestions and the **How these suggestions are generated** methodology card. Open a saved plan and, if it is **completed**, use **Review observed counts** with two valid equal-length ordered date windows. No claim of causal effectiveness. |
| **4:00–4:30** | **User management** *(Admin only)* | Show roles and selected audit history. Explain that Admin can manage accounts; Viewer, Analyst and Officer have narrower privileges, enforced by the backend. Skip if signed in as Officer. |
| **4:30–5:00** | **Analytics → Build presentation PDF** | Expand the report panel, select analytics/spatial/prevention sections, and download the combined PDF. Close: **Record → Map → Analyse → Prevent → Review → Present**, with a single HTTPS service and persistent cloud database. |

**Avoid modifying the shared cloud demo data during the talk.** The **Import incident data** flow supports read-only CSV/JSON validation and duplicate review before confirmation; you can show the preview and cancel when asked about imports. If you need a saved plan to explain the lifecycle, prepare it beforehand rather than rushing to create and complete one live.

### One-sentence technical explanation

“CrimeMap uses a **multi-stage Docker build**: Node.js compiles the React/Vite frontend, and a smaller Python image serves those compiled assets and FastAPI through **one Google Cloud Run HTTPS service**; **Cloud SQL PostgreSQL** stores users and incidents persistently, **Secret Manager** supplies database credentials, and **GitHub Actions** checks the build and application.”

## Likely judge questions

**Is this crime prediction or real police intelligence?** No. Heatmaps, grid comparisons, incident analytics and before/later plan reviews show **descriptive counts of synthetic data**. Real analysis would require authorized data, governance and independent validation.

**Are the zones or operational overlays real?** No. Demonstration zones use fictional reference points; patrol/CCTV-style overlays are simulations. The basemap uses OpenStreetMap tiles.

**Where does a newly created user or imported incident go?** On the deployed site, it is stored in the `crimemap` **Cloud SQL PostgreSQL** database. Passwords are stored as hashes, not plaintext. Confirmed incidents/plans remain after Cloud Run restarts or code redeployments. A local `python3 start.py` session ordinarily uses **separate SQLite data**.

**How do you avoid duplicate imports?** The import preview validates data and flags possible matches using category, occurrence timestamp (UTC second) and coordinates rounded to six decimals. These are heuristics, not proven duplicate identities. Import preview **does not write data**.

**Why Cloud Run and a multi-stage Dockerfile?** The Node.js stage compiles React; the final Python runtime image serves both frontend and API without shipping the development Vite server. Cloud Run manages HTTPS and scaling; Cloud SQL is separate so users/incidents are **not stored in the ephemeral container filesystem**.

**Does an app account mean access is publicly open?** No. **Cloud Run IAM** decides whether a browser can reach the HTTPS service at all; the separate **CrimeMap login and roles** control application permissions after that. The access setting must be intentionally chosen for the synthetic-only demo.

**What makes it persistent, and is it production ready?** Cloud SQL stores application records independently of Cloud Run revisions. Persistence is not proof of production readiness: this demo still needs security/privacy review, backups/migrations, authorized operational data, and production identity and auditing controls.

**Does marking a prevention plan completed prove it worked?** No. The earlier/later review uses manually selected windows without a control group or causal attribution.

## If the internet or Cloud Run fails

**Do not start resetting the cloud database on stage.** Show the saved synthetic PDF/screenshots and continue the story, or use the pre-tested local backup below. Avoid treating a `403` as a database failure; check Cloud Run IAM access separately.

The **local fallback** is *not the same database* and may show different users, plan statuses and incident totals. Prepare it before arriving, not during the talk. From a clean, already configured local clone:

```bash
# First refresh frontend dependencies if Tailwind/Vite packages have changed:
cd frontend
npm ci
cd ..

# Uses the existing local SQLite database and existing local account.
python3 start.py
# Open http://127.0.0.1:5173 ; backend health: http://127.0.0.1:8000/health
```

If `npm ci` was run beforehand and nothing changed, only `python3 start.py` is needed. **Never delete `backend/crimemap.db` or rebootstrap local accounts** as a troubleshooting shortcut. On Windows use the already configured `start_windows.bat`.

## Manual readiness checklist

These are **on-site checks**; CI does not verify your projector, network, Cloud Run IAM setting or current cloud database state.

- [ ] Cloud Run site loads and an existing **cloud** account signs in; check the desired access setting ahead of time.
- [ ] Light mode is readable from the back of the room, and the dark mode toggle still works.
- [ ] All four workspaces load, the incident **Map** action highlights a record, and both map tiles and grid comparisons render.
- [ ] Analytics loads with realistic current *fictional* counts, and a presentation PDF downloads successfully.
- [ ] The Prevention methodology card is readable; a completed plan is prepared if showcasing the count review.
- [ ] Admin-only user management/audit history is available **if** the presenter is using an admin account.
- [ ] Imported records or test accounts, **if intentionally created**, persist after refresh; do not change or reset shared demo data unnecessarily.
- [ ] Mobile/keyboard basics (nav access, focus, dialogs, import picker) work if you plan to show them.
- [ ] Backup PDF/screenshots and an optional **pre-tested local** demo are ready; the differences between cloud PostgreSQL and local SQLite are understood.
- [ ] Synthetic-data warnings remain visible. No claim of real police intelligence, official jurisdiction mapping, actual operational feeds, crime prediction or proven prevention impact.

See [Cloud Run + Cloud SQL deployment handoff](CLOUD_DEPLOYMENT.md) for resource inventory, deployment updates, security and costs, and [Developer setup / data safety](SETUP.md) for the independent local fallback.
