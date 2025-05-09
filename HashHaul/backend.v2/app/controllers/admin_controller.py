from flask import jsonify
from app.models.viaje_model import Viaje
from app.models.incidente_model import Incidente

def resumen_dashboard():
    viajes_activos = Viaje.query.filter_by(estado="activo").count()
    viajes_pendientes = Viaje.query.filter_by(estado="pendiente").count()
    viajes_fallidos = Viaje.query.filter_by(estado="fallido").count()

    incidentes = Incidente.query.count()

    return jsonify({
        "viajes_activos": viajes_activos,
        "viajes_pendientes": viajes_pendientes,
        "viajes_fallidos": viajes_fallidos,
        "incidentes": incidentes
    }), 200
