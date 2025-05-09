from flask import Blueprint, jsonify
from app.services.blockchain_service import cargar_contrato

blockchain_bp = Blueprint("blockchain", __name__)

@blockchain_bp.route('/ver_checkpoint/<int:id>', methods=['GET'])
def ver_checkpoint(id):
    try:
        contract = cargar_contrato()
        # Llama a la función del contrato, por ejemplo: obtenerEstadoCheckpoint(uint id)
        estado = contract.functions.obtenerEstadoCheckpoint(id).call()
        return jsonify({"estado": estado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
