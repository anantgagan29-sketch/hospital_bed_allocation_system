# Deployment Notes

## Local / normal server (recommended for the viva)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 database/init_db.py
python3 app.py
```

The database lives at `database/hospital.db` on disk and survives restarts,
exactly like a real deployment on a normal server (Render, Railway, your
own Linux machine, etc.) would.

## Vercel

`vercel.json` is included so Vercel can build and run `app.py` as a Python
WSGI app. Two things had to change specifically for Vercel's environment:

1. **Database location.** Vercel's filesystem is **read-only** at runtime
   except for `/tmp`, and the project's actual `database/hospital.db` file
   is intentionally excluded from the repo (`.gitignore`) since it's local
   demo data. `config.py` detects `VERCEL=1` (Vercel sets this
   automatically) and points `DATABASE_PATH` at `/tmp/hospital.db` instead.
2. **Auto-initialization.** `app.py::ensure_database()` creates the
   database from `database/schema.sql` + `seed_data.sql` automatically if
   it doesn't already exist at `DATABASE_PATH`.

### Important limitation — data does not persist on Vercel

Vercel runs this app as **serverless functions**: each request can be
handled by a fresh, isolated container, and `/tmp` is wiped whenever a new
one spins up (a "cold start"). That means:

- Patients/beds/requests you create can disappear and reset back to the
  20-bed seed data at any time, with no warning.
- Two requests happening close together might even hit *different*
  containers with *different* databases.

This is a fundamental mismatch between Vercel's stateless serverless model
and this app's design (a normal, always-running server with a real local
database file) — not a bug to "fix" further without changing the
database technology (e.g. to a hosted Postgres). For a **reliable**, always-
persistent live demo, deploy instead to a platform that runs the app as a
continuously-running process with a real disk, such as Render.com,
Railway, or PythonAnywhere — the exact same code and `requirements.txt`
work there unmodified (no `vercel.json` needed).

For the OS PBL viva itself, the important thing evaluators check is the
running behaviour and the code — a Vercel link is a convenience, not a
requirement.
