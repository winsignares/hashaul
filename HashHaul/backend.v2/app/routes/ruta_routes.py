from flask import Blueprint
from app.controllers.ruta_controller import listar_rutas, obtener_ruta, crear_ruta, actualizar_ruta, eliminar_ruta

ruta_bp = Blueprint("rutas", __name__)

ruta_bp.route("/rutas", methods=["GET"])(listar_rutas)
ruta_bp.route("/rutas/<int:ruta_id>", methods=["GET"])(obtener_ruta)
ruta_bp.route("/rutas", methods=["POST"])(crear_ruta)
ruta_bp.route("/rutas/<int:ruta_id>", methods=["PUT"])(actualizar_ruta)
ruta_bp.route("/rutas/<int:ruta_id>", methods=["DELETE"])(eliminar_ruta)
