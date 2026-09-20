from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.db import get_db
from models import patients as patient_model

patient_bp = Blueprint("patients", __name__)


@patient_bp.route("/patients", methods=["GET", "POST"])
def patients():
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        condition = request.form.get("medical_condition", "").strip()
        contact = request.form.get("contact", "").strip()

        if not name or not age.isdigit():
            flash("Name and a valid age are required.", "error")
        else:
            patient_id = patient_model.create_patient(db, name, int(age), gender, condition, contact)
            flash(f"Patient registered with ID {patient_id}.", "success")
        return redirect(url_for("patients.patients"))

    return render_template("patients.html", patients=patient_model.list_patients(db))
