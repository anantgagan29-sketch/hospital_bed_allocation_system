"""
Hospital Bed Allocation Platform — Flask entry point.

The website itself only exposes hospital-facing pages (dashboard,
patients, beds, requests, history). The Operating Systems engineering —
CPU scheduling, the PCB/process lifecycle, and the allocation lock — is
not a separate demo section: it runs internally on every request, inside
routes/request_routes.py and services/allocation_service.py. See
docs/OS_CONCEPT_MAPPING.md and docs/Linux_Commands_and_OS_Concepts_Explained.pdf
for exactly where each concept lives in the code.

Application-level note: when this file calls app.run(), Flask asks the
Linux kernel (via the OS's socket and process facilities) to open a
listening socket and, for each request, hands work to a worker thread.
"""
import os

from flask import Flask, redirect, url_for

import config
from database.init_db import init_db
from models.db import close_db
from routes.dashboard_routes import dashboard_bp
from routes.patient_routes import patient_bp
from routes.bed_routes import bed_bp
from routes.request_routes import request_bp
from routes.history_routes import history_bp


def ensure_database() -> None:
    """Create the database if it doesn't exist yet. Locally this only runs
    once, ever (the file persists). On Vercel, config.DATABASE_PATH points
    at /tmp, which is wiped on every cold start, so this recreates a fresh
    demo database each time a new container starts up."""
    if not os.path.exists(config.DATABASE_PATH):
        init_db()


def create_app() -> Flask:
    ensure_database()

    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    app.teardown_appcontext(close_db)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(bed_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(history_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard"))

    return app


app = create_app()

if __name__ == "__main__":
    # Port 5000 is taken by AirPlay Receiver on many Macs — override with
    # PORT=5001 python3 app.py if you hit "Address already in use".
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
