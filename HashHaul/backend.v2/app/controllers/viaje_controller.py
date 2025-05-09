from flask import jsonify, request
from app.models.viaje_model import Viaje
from app.models.camion_model import Camion
from app.models.usuario_model import Usuario
from app.database.db import db

def historial_viajes(usuario_id):
    viajes_completados = Viaje.query.filter_by(usuario_id=usuario_id, estado='completado').all()

    if not viajes_completados:
        return jsonify({"error": "No hay viajes completados para este conductor"}), 404

    return jsonify([
        {
            "id": v.id,
            "camion_id": v.camion_id,
            "estado": v.estado,
        } for v in viajes_completados
    ]), 200

def proximos_viajes(usuario_id):
    viajes_proximos = Viaje.query.filter(
        Viaje.usuario_id == usuario_id,
        Viaje.estado.in_(['pendiente', 'en curso'])
    ).all()

    if not viajes_proximos:
        return jsonify({"error": "No hay viajes pendientes o en curso para este conductor"}), 404

    return jsonify([
        {
            "id": v.id,
            "camion_id": v.camion_id,
            "estado": v.estado,
        } for v in viajes_proximos
    ]), 200

def listar_viajes():
    viajes = Viaje.query.all()
    return jsonify([
        {
            "id": v.id,
            "usuario_id": v.usuario_id,
            "camion_id": v.camion_id,
            "estado": v.estado
        } for v in viajes
    ]), 200

# Ver un viaje específico
def obtener_viaje(viaje_id):
    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return jsonify({"error": "Viaje no encontrado"}), 404

    return jsonify({
        "id": viaje.id,
        "usuario_id": viaje.usuario_id,
        "camion_id": viaje.camion_id,
        "estado": viaje.estado
    }), 200

# Crear un nuevo viaje
def crear_viaje():
    data = request.get_json()
    usuario_id = data.get("usuario_id")
    camion_id = data.get("camion_id")

    usuario = Usuario.query.get(usuario_id)
    camion = Camion.query.get(camion_id)

    if not usuario or not camion:
        return jsonify({"error": "Usuario o camión no encontrado"}), 404

    viaje = Viaje(usuario_id=usuario_id, camion_id=camion_id)
    db.session.add(viaje)
    db.session.commit()

    return jsonify({"mensaje": "Viaje creado", "viaje_id": viaje.id}), 201

# Actualizar un viaje
def actualizar_viaje(viaje_id):
    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return jsonify({"error": "Viaje no encontrado"}), 404

    data = request.get_json()
    viaje.estado = data.get("estado", viaje.estado)
    db.session.commit()

    return jsonify({"mensaje": "Viaje actualizado", "estado": viaje.estado}), 200

# Eliminar un viaje
def eliminar_viaje(viaje_id):
    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return jsonify({"error": "Viaje no encontrado"}), 404

    db.session.delete(viaje)
    db.session.commit()

    return jsonify({"mensaje": "Viaje eliminado"}), 200


