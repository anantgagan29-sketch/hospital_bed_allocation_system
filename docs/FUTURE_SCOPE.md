# Future Scope

The current build satisfies every requirement in the assignment brief.
These are honest next steps — things intentionally left out to keep the
first version focused, not things that are broken.

## More OS concepts to add

- **Deadlock detection/avoidance demo.** Right now only one lock exists
  per manager, so deadlock can't occur (see docs/CONCURRENCY.md). A
  future version could add a second shared resource (e.g. "equipment"
  alongside "beds") and deliberately show a Resource Allocation Graph
  with a cycle, then a Banker's Algorithm-style avoidance check.
- **Memory management simulation.** Paging/segmentation aren't covered
  yet. A simple visual demo (fixed-size "pages" of a patient record
  being mapped to "frames") would extend the OS coverage into Unit 3.
- **Multi-Level Feedback Queue (MLFQ) scheduling** as a sixth algorithm,
  showing how real OS schedulers combine several queues with different
  priorities and quanta.
- **Inter-Process Communication (IPC).** A second background process
  (e.g. a notification worker) communicating with the main app via a
  pipe or `multiprocessing.Queue` would demonstrate IPC concretely.

## Real-world hospital features

- **Login & roles** — separate accounts for admin, doctor, and nurse,
  each with different permissions (e.g. only admin can discharge).
- **SMS/email alerts** to a waiting patient's contact the moment a bed
  frees up for them.
- **Multi-hospital support** — the same platform managing several
  hospitals' bed pools separately.
- **Predictive analytics** — a simple model estimating bed demand from
  historical allocation data, to plan capacity ahead of time.

## Technical / production improvements

- **A real database engine** (PostgreSQL/MySQL) in place of SQLite for
  multi-user concurrent write scale — SQLite is intentionally used here
  for simplicity per the course brief, but wouldn't scale to a real
  hospital's write volume.
- **Deploy on a platform built for a persistent server** (Render,
  Railway, PythonAnywhere) instead of Vercel's serverless model — see
  docs/DEPLOYMENT.md for why Vercel resets data between cold starts.
- **Automated CI** — run `pytest tests/` automatically via GitHub Actions
  on every push, so a broken commit never reaches `main`.
- **Live dashboard updates** via WebSockets, instead of requiring a page
  refresh to see a newly allocated bed.

## What deliberately stays out of scope

Per the course brief's own guidance (avoid unnecessary complexity):
React, Docker, Kubernetes, Redis, and microservices are not planned,
even for a "v2" — they would teach infrastructure concepts unrelated to
this course's Operating Systems syllabus.
