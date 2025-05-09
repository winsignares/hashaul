from flask import Blueprint
from app.controllers.perfil_controller import obtener_perfil

perfil_bp = Blueprint("perfil", __name__)

perfil_bp.route("/conductor/<int:usuario_id>/perfil", methods=["GET"])(obtener_perfil)
