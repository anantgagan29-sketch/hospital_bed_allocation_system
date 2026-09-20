from flask import Blueprint, render_template

from models.db import get_db
from models import beds as bed_model
from models import requests as request_model
from models import processes as process_model

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    db = get_db()

    bed_counts = bed_model.counts_by_status(db)
    all_requests = request_model.list_requests(db)
    all_processes = process_model.list_processes(db)

    waiting_requests = [r for r in all_requests if r["status"] == "WAITING"]
    critical_requests = [r for r in all_requests if r["urgency"] == "CRITICAL" and r["status"] != "ALLOCATED"]
    active_processes = [p for p in all_processes if p["state"] != "TERMINATED"]
    completed = [r for r in all_requests if r["status"] == "ALLOCATED"]

    cards = {
        "total_beds": sum(bed_counts.values()),
        "available_beds": bed_counts["AVAILABLE"],
        "occupied_beds": bed_counts["ALLOCATED"],
        "waiting_requests": len(waiting_requests),
        "critical_requests": len(critical_requests),
        "active_processes": len(active_processes),
        "completed_allocations": len(completed),
    }

    type_rows = bed_model.counts_by_type(db)
    by_type = {}
    for row in type_rows:
        by_type.setdefault(row["type"], {"AVAILABLE": 0, "ALLOCATED": 0, "MAINTENANCE": 0})
        by_type[row["type"]][row["status"]] = row["n"]

    urgency_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in all_requests:
        urgency_counts[r["urgency"]] = urgency_counts.get(r["urgency"], 0) + 1

    bed_type_request_counts = {}
    for r in all_requests:
        bed_type_request_counts[r["required_bed_type"]] = bed_type_request_counts.get(r["required_bed_type"], 0) + 1

    return render_template(
        "dashboard.html",
        cards=cards,
        by_type=by_type,
        urgency_counts=urgency_counts,
        bed_type_request_counts=bed_type_request_counts,
        recent_requests=all_requests[-8:][::-1],
    )
