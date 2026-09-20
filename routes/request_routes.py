from flask import Blueprint, render_template, request, redirect, url_for, flash

import config
from models.db import get_db
from models import requests as request_model
from models import patients as patient_model
from services import scheduler, allocation_service

request_bp = Blueprint("requests", __name__)

# Internal scheduling input. This is NOT a medical duration -- it is a fixed,
# deliberately simple estimate of "how long the allocation engine takes to
# process this request", used only so the CPU-scheduling algorithm has a
# burst_time to work with. See docs/SCHEDULING.md.
DEFAULT_BURST_TIME = 5


@request_bp.route("/requests", methods=["GET", "POST"])
def requests_page():
    db = get_db()

    if request.method == "POST":
        patient_id = request.form.get("patient_id", "").strip()
        urgency = request.form.get("urgency", "")
        bed_type = request.form.get("required_bed_type", "")

        patient = patient_model.get_patient(db, patient_id)
        if patient is None:
            flash("Select a valid registered patient.", "error")
        elif urgency not in config.URGENCY_LEVELS:
            flash("Select a valid urgency level.", "error")
        elif bed_type not in config.BED_TYPES:
            flash("Select a valid bed type.", "error")
        else:
            request_id = request_model.create_request(
                db, patient["patient_id"], patient["name"], patient["age"],
                patient["medical_condition"], urgency, bed_type, DEFAULT_BURST_TIME,
            )

            # Internally: order every currently pending/waiting request by
            # urgency (Priority scheduling) and attempt a real bed allocation
            # for each, in that order. This is the same scheduler + PCB +
            # allocation-lock engine described in docs/OS_CONCEPT_MAPPING.md --
            # it just runs automatically instead of through a separate page.
            result = scheduler.run(db, "PRIORITY")
            outcomes = allocation_service.execute_schedule(db, result) if result else []
            own_outcome = next((o for o in outcomes if o["request_id"] == request_id), None)

            if own_outcome and own_outcome["allocated"]:
                flash(f"Request {request_id} created — bed {own_outcome['bed_id']} allocated immediately.",
                      "success")
            else:
                flash(f"Request {request_id} created — no {bed_type} bed free right now, "
                      f"added to the waiting list.", "success")
        return redirect(url_for("requests.requests_page"))

    return render_template(
        "requests.html",
        requests=list(reversed(request_model.list_requests(db))),
        patients=patient_model.list_patients(db),
        urgency_levels=config.URGENCY_LEVELS,
        bed_types=config.BED_TYPES,
    )
