from flask import Blueprint
from app.controllers.checkpoint_controller import obtener_checkpoints, obtener_todos_checkpoints, obtener_checkpoint, crear_checkpoint, actualizar_checkpoint, eliminar_checkpoint

checkpoint_bp = Blueprint("checkpoints", __name__)

checkpoint_bp.route("/viaje/<int:viaje_id>/checkpoints", methods=["GET"])(obtener_checkpoints)


checkpoint_bp.route("/checkpoints", methods=["GET"])(obtener_todos_checkpoints)
checkpoint_bp.route("/checkpoint/<int:id>", methods=["GET"])(obtener_checkpoint)
checkpoint_bp.route("/checkpoint", methods=["POST"])(crear_checkpoint)
checkpoint_bp.route("/checkpoint/<int:id>", methods=["PUT"])(actualizar_checkpoint)
checkpoint_bp.route("/checkpoint/<int:id>", methods=["DELETE"])(eliminar_checkpoint)


