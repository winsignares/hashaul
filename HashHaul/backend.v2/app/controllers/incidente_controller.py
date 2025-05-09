from flask import request, jsonify
from app.models.checkpoint_model import Checkpoint
from app.models.incidente_model import Incidente
from app.database.db import db

def registrar_incidente(checkpoint_id):
    checkpoint = Checkpoint.query.get(checkpoint_id)
    if not checkpoint:
        return jsonify({"error": "Checkpoint no encontrado"}), 404

    data = request.get_json()
    descripcion = data.get("descripcion")

    if not descripcion:
        return jsonify({"error": "La descripción es obligatoria"}), 400

    checkpoint.estado = "fallido"

    incidente = Incidente(descripcion=descripcion, checkpoint_id=checkpoint_id)
    db.session.add(incidente)
    db.session.commit()

    return jsonify({
        "mensaje": "Incidente registrado y checkpoint marcado como fallido",
        "incidente": {
            "id": incidente.id,
            "descripcion": incidente.descripcion,
            "timestamp": incidente.timestamp
        }
    }), 201

def listar_incidentes():
    incidentes = Incidente.query.all()
    return jsonify([
        {
            "id": i.id,
            "descripcion": i.descripcion,
            "timestamp": i.timestamp,
            "checkpoint_id": i.checkpoint_id
        } for i in incidentes
    ]), 200

def obtener_incidente(incidente_id):
    incidente = Incidente.query.get(incidente_id)
    if not incidente:
        return jsonify({"error": "Incidente no encontrado"}), 404

    return jsonify({
        "id": incidente.id,
        "descripcion": incidente.descripcion,
        "timestamp": incidente.timestamp,
        "checkpoint_id": incidente.checkpoint_id
    }), 200

