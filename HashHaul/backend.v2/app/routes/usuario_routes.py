from flask import Blueprint
from app.controllers.usuario_controller import (
    obtener_usuarios,
    obtener_usuario,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario
)

usuario_bp = Blueprint("usuarios", __name__)

usuario_bp.route("/admin/usuarios", methods=["GET"])(obtener_usuarios)
usuario_bp.route("/admin/usuarios/<int:id>", methods=["GET"])(obtener_usuario)
usuario_bp.route("/admin/usuarios", methods=["POST"])(crear_usuario)
usuario_bp.route("/admin/usuarios/<int:id>", methods=["PUT"])(actualizar_usuario)
usuario_bp.route("/admin/usuarios/<int:id>", methods=["DELETE"])(eliminar_usuario)
