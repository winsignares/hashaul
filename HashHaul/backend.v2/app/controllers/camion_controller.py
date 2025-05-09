from flask import jsonify, request
from app.models.camion_model import Camion
from app.models.viaje_model import Viaje
from app.database.db import db

# conductor
def listar_camiones_asignados(usuario_id):
    viajes = Viaje.query.filter_by(usuario_id=usuario_id).all()

    camiones_vistos = {}
    for viaje in viajes:
        camion = viaje.camion
        if camion and camion.id not in camiones_vistos:
            camiones_vistos[camion.id] = {
                "id": camion.id,
                "placa": camion.placa,
                "modelo": camion.modelo
            }

    return jsonify(list(camiones_vistos.values()))

# admind crud
def obtener_camiones():
    camiones = Camion.query.all()
    return jsonify([
        {"id": c.id, "placa": c.placa, "modelo": c.modelo}
        for c in camiones
    ])

def obtener_camion(id):
    camion = Camion.query.get(id)
    if not camion:
        return jsonify({"error": "Camión no encontrado"}), 404
    return jsonify({
        "id": camion.id,
        "placa": camion.placa,
        "modelo": camion.modelo
    })

def crear_camion():
    data = request.get_json()
    placa = data.get("placa")
    modelo = data.get("modelo")

    if not placa or not modelo:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    nuevo_camion = Camion(placa=placa, modelo=modelo)
    db.session.add(nuevo_camion)
    db.session.commit()

    return jsonify({"mensaje": "Camión creado", "id": nuevo_camion.id}), 201

def actualizar_camion(id):
    camion = Camion.query.get(id)
    if not camion:
        return jsonify({"error": "Camión no encontrado"}), 404

    data = request.get_json()
    camion.placa = data.get("placa", camion.placa)
    camion.modelo = data.get("modelo", camion.modelo)

    db.session.commit()
    return jsonify({"mensaje": "Camión actualizado"})

def eliminar_camion(id):
    camion = Camion.query.get(id)
    if not camion:
        return jsonify({"error": "Camión no encontrado"}), 404

    db.session.delete(camion)
    db.session.commit()
    return jsonify({"mensaje": "Camión eliminado"})
