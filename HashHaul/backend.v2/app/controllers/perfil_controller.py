from flask import jsonify
from app.models.usuario_model import Usuario

def obtener_perfil(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "telefono": usuario.telefono if hasattr(usuario, "telefono") else None,
        "rol": usuario.rol
    }), 200

