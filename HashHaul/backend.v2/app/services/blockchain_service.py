from web3 import Web3
import json
import hashlib

# Conectar con Ganache
ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Verificar conexión
if not w3.is_connected():
    raise ConnectionError("No se pudo conectar a Ganache")

# Establecer la cuenta por defecto
w3.eth.default_account = w3.eth.accounts[0]

# Ruta al contrato compilado y dirección del contrato desplegado
CONTRACT_PATH = "contracts/compiled_contract.json"
CONTRACT_ADDRESS = "0x148e144d06f5e94b7044490bBDe43d1A3bf440d4"  # Actualiza esto si cambia

def cargar_contrato():
    with open(CONTRACT_PATH, "r") as f:
        compiled_contract = json.load(f)

    abi = compiled_contract["abi"]

    contrato = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    return contrato

def generar_hash_checkpoint(direccion, latitud, longitud):
    """
    Genera un hash SHA-256 usando dirección + latitud + longitud.
    """
    datos = f"{direccion}{latitud}{longitud}".encode("utf-8")
    return hashlib.sha256(datos).hexdigest()
