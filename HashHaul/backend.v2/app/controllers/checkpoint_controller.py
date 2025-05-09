from flask import jsonify, request
from app.models.checkpoint_model import Checkpoint
from app.models.ruta_model import Ruta
from app.database.db import db
from web3 import Web3
from app.services.blockchain_service import generar_hash_checkpoint

# ---------- Conductor ----------
def obtener_checkpoints(viaje_id):
    checkpoints = Checkpoint.query.join(Checkpoint.ruta).filter_by(viaje_id=viaje_id).all()

    if not checkpoints:
        return jsonify({"error": "No hay checkpoints para este viaje"}), 404

    return jsonify([
        {
            "id": c.id,
            "direccion": c.direccion,
            "latitud": c.latitud,
            "longitud": c.longitud,
            "estado": c.estado,
            "hash": c.hash,
        } for c in checkpoints
    ]), 200

# ---------- Administrador (CRUD) ----------
def obtener_todos_checkpoints():
    checkpoints = Checkpoint.query.all()
    return jsonify([
        {
            "id": c.id,
            "direccion": c.direccion,
            "latitud": c.latitud,
            "longitud": c.longitud,
            "estado": c.estado,
            "hash": c.hash,  # Mostrar el hash de cada checkpoint
            "ruta_id": c.ruta_id
        } for c in checkpoints
    ])

def obtener_checkpoint(id):
    checkpoint = Checkpoint.query.get(id)
    if not checkpoint:
        return jsonify({"error": "Checkpoint no encontrado"}), 404

    return jsonify({
        "id": checkpoint.id,
        "direccion": checkpoint.direccion,
        "latitud": checkpoint.latitud,
        "longitud": checkpoint.longitud,
        "estado": checkpoint.estado,
        "hash": checkpoint.hash,  # Mostrar el hash del checkpoint
        "ruta_id": checkpoint.ruta_id
    })


def crear_checkpoint():
    data = request.get_json()
    direccion = data.get("direccion")
    latitud = data.get("latitud")
    longitud = data.get("longitud")
    estado = data.get("estado", "pendiente")
    ruta_id = data.get("ruta_id")

    if not direccion or not latitud or not longitud or not ruta_id:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    hash_generado = generar_hash_checkpoint({
        "direccion": direccion,
        "latitud": latitud,
        "longitud": longitud,
        "estado": estado
    })

    nuevo_checkpoint = Checkpoint(
        direccion=direccion,
        latitud=latitud,
        longitud=longitud,
        estado=estado,
        ruta_id=ruta_id,
        hash=hash_generado
    )
    db.session.add(nuevo_checkpoint)
    db.session.commit()

    return jsonify({"mensaje": "Checkpoint creado", "id": nuevo_checkpoint.id, "hash": hash_generado}), 201

def actualizar_checkpoint(id):
    checkpoint = Checkpoint.query.get(id)
    if not checkpoint:
        return jsonify({"error": "Checkpoint no encontrado"}), 404

    data = request.get_json()
    checkpoint.direccion = data.get("direccion", checkpoint.direccion)
    checkpoint.latitud = data.get("latitud", checkpoint.latitud)
    checkpoint.longitud = data.get("longitud", checkpoint.longitud)
    checkpoint.estado = data.get("estado", checkpoint.estado)
    checkpoint.ruta_id = data.get("ruta_id", checkpoint.ruta_id)

    # Volver a generar el hash del checkpoint luego de actualizarlo
    checkpoint.hash = checkpoint.generar_hash()

    # Lógica para registrar la actualización en la blockchain (si es necesario)
    tx_hash = registrar_en_blockchain(checkpoint)

    # Si se ha registrado la transacción en la blockchain, guardamos el hash de la transacción
    checkpoint.blockchain_tx_hash = tx_hash

    db.session.commit()
    return jsonify({"mensaje": "Checkpoint actualizado", "hash": checkpoint.hash})

def eliminar_checkpoint(id):
    checkpoint = Checkpoint.query.get(id)
    if not checkpoint:
        return jsonify({"error": "Checkpoint no encontrado"}), 404

    db.session.delete(checkpoint)
    db.session.commit()
    return jsonify({"mensaje": "Checkpoint eliminado"})


# Función para registrar en la blockchain
def registrar_en_blockchain(checkpoint):
    # Aquí implementas la lógica para interactuar con la blockchain usando Web3.py
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
    contract = w3.eth.contract(address='0xYourContractAddress', abi=contract_abi)

    # Asumimos que el contrato tiene un método para registrar un checkpoint
    # Debes definir la lógica aquí dependiendo de tu contrato inteligente
    tx = contract.functions.registrarCheckpoint(
        checkpoint.direccion,
        checkpoint.latitud,
        checkpoint.longitud,
        checkpoint.estado,
        checkpoint.hash
    ).buildTransaction({
        'chainId': 1,  # Mainnet
        'gas': 2000000,
        'gasPrice': w3.toWei('10', 'gwei'),
        'nonce': w3.eth.getTransactionCount('YOUR_WALLET_ADDRESS'),
    })

    # Firmar la transacción (asegúrate de tener una wallet configurada)
    private_key = "YOUR_PRIVATE_KEY"
    signed_tx = w3.eth.account.signTransaction(tx, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # Retornar el hash de la transacción en la blockchain
    return tx_hash.hex()


