from flask import Blueprint
from app.controllers.admin_controller import resumen_dashboard

admin_bp = Blueprint("admin", __name__)

admin_bp.route("/admin/resumen", methods=["GET"])(resumen_dashboard)
