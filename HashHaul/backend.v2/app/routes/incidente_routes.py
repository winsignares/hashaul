from flask import Blueprint
from app.controllers.incidente_controller import registrar_incidente, obtener_incidente, listar_incidentes

incidente_bp = Blueprint("incidentes", __name__)
incidente_bp.route("/checkpoints/<int:checkpoint_id>/incidente", methods=["POST"])(registrar_incidente)

incidente_bp.route("/incidentes", methods=["GET"])(listar_incidentes)
incidente_bp.route("/incidentes/<int:incidente_id>", methods=["GET"])(obtener_incidente)


