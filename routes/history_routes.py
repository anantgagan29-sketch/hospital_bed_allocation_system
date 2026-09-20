from flask import Blueprint, render_template

from models.db import get_db
from models import history as history_model

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
def history():
    db = get_db()
    return render_template(
        "history.html",
        allocation_history=history_model.list_history(db),
        system_logs=history_model.list_logs(db),
    )
