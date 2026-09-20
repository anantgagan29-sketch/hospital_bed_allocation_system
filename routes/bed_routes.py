from flask import Blueprint, render_template, request, redirect, url_for, flash

import config
from models.db import get_db
from models import beds as bed_model
from services import allocation_service

bed_bp = Blueprint("beds", __name__)


@bed_bp.route("/beds")
def beds():
    db = get_db()
    return render_template("beds.html", beds=bed_model.list_beds(db), bed_types=config.BED_TYPES)


@bed_bp.route("/beds/<bed_id>/maintenance", methods=["POST"])
def toggle_maintenance(bed_id):
    db = get_db()
    bed = bed_model.get_bed(db, bed_id)
    if bed is None:
        flash("Bed not found.", "error")
    elif bed["status"] == "ALLOCATED":
        flash("Cannot set an allocated bed to maintenance — discharge the patient first.", "error")
    else:
        bed_model.set_maintenance(db, bed_id, bed["status"] != "MAINTENANCE")
        db.commit()
        flash(f"Bed {bed_id} updated.", "success")
    return redirect(url_for("beds.beds"))


@bed_bp.route("/beds/<bed_id>/discharge", methods=["POST"])
def discharge(bed_id):
    db = get_db()
    outcome = allocation_service.discharge(db, bed_id)
    if not outcome["released"]:
        flash("Bed is not currently allocated.", "error")
    elif outcome["reallocated_to"]:
        flash(f"Bed {bed_id} released and immediately reallocated to {outcome['reallocated_to']} "
              f"(a waiting request).", "success")
    else:
        flash(f"Bed {bed_id} released and is now available.", "success")
    return redirect(url_for("beds.beds"))
