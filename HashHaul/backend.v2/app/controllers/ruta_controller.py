from flask import jsonify, request
from app.models.ruta_model import Ruta
from app.models.viaje_model import Viaje
from app.database.db import db

# Ver todas las rutas
def listar_rutas():
    rutas = Ruta.query.all()
    return jsonify([
        {
            "id": r.id,
            "viaje_id": r.viaje_id
        } for r in rutas
    ]), 200

# Ver una ruta específica
def obtener_ruta(ruta_id):
    ruta = Ruta.query.get(ruta_id)
    if not ruta:
        return jsonify({"error": "Ruta no encontrada"}), 404

    return jsonify({
        "id": ruta.id,
        "viaje_id": ruta.viaje_id
    }), 200

# Crear una nueva ruta
def crear_ruta():
    data = request.get_json()
    viaje_id = data.get("viaje_id")

    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return jsonify({"error": "Viaje no encontrado"}), 404

    ruta = Ruta(viaje_id=viaje_id)
    db.session.add(ruta)
    db.session.commit()

    return jsonify({"mensaje": "Ruta creada", "ruta_id": ruta.id}), 201

# Actualizar una ruta
def actualizar_ruta(ruta_id):
    ruta = Ruta.query.get(ruta_id)
    if not ruta:
        return jsonify({"error": "Ruta no encontrada"}), 404

    data = request.get_json()
    ruta.viaje_id = data.get("viaje_id", ruta.viaje_id)
    db.session.commit()

    return jsonify({"mensaje": "Ruta actualizada", "viaje_id": ruta.viaje_id}), 200

# Eliminar una ruta
def eliminar_ruta(ruta_id):
    ruta = Ruta.query.get(ruta_id)
    if not ruta:
        return jsonify({"error": "Ruta no encontrada"}), 404

    db.session.delete(ruta)
    db.session.commit()

    return jsonify({"mensaje": "Ruta eliminada"}), 200
