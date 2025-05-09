from flask import jsonify
from app.services.blockchain_service import cargar_contrato

def ver_estado_checkpoint(checkpoint_id):
    try:
        contrato = cargar_contrato()
        estado = contrato.functions.obtenerEstadoCheckpoint(checkpoint_id).call()
        return jsonify({"estado": estado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
