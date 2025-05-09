from flask import Blueprint
from app.controllers.camion_controller import (
    listar_camiones_asignados,
    obtener_camiones,
    obtener_camion,
    crear_camion,
    actualizar_camion,
    eliminar_camion
)

camion_bp = Blueprint("camiones", __name__)

# conductor
camion_bp.route("/conductor/<int:usuario_id>/camiones", methods=["GET"])(listar_camiones_asignados)

# admin
camion_bp.route("/admin/camiones", methods=["GET"])(obtener_camiones)
camion_bp.route("/admin/camiones/<int:id>", methods=["GET"])(obtener_camion)
camion_bp.route("/admin/camiones", methods=["POST"])(crear_camion)
camion_bp.route("/admin/camiones/<int:id>", methods=["PUT"])(actualizar_camion)
camion_bp.route("/admin/camiones/<int:id>", methods=["DELETE"])(eliminar_camion)
