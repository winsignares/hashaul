from flask import Blueprint
from app.controllers.viaje_controller import (
    historial_viajes,
    proximos_viajes,
    listar_viajes,
    obtener_viaje,
    crear_viaje,
    actualizar_viaje,
    eliminar_viaje
)

viaje_bp = Blueprint("viajes", __name__)

viaje_bp.route("/conductor/<int:usuario_id>/historial_viajes", methods=["GET"])(historial_viajes)
viaje_bp.route("/conductor/<int:usuario_id>/proximos_viajes", methods=["GET"])(proximos_viajes)

viaje_bp.route("/viajes", methods=["GET"])(listar_viajes)
viaje_bp.route("/viajes/<int:viaje_id>", methods=["GET"])(obtener_viaje)
viaje_bp.route("/viajes", methods=["POST"])(crear_viaje)
viaje_bp.route("/viajes/<int:viaje_id>", methods=["PUT"])(actualizar_viaje)
viaje_bp.route("/viajes/<int:viaje_id>", methods=["DELETE"])(eliminar_viaje)