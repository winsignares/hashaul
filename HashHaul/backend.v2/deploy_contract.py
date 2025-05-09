from solcx import compile_source, install_solc
from web3 import Web3
import json

# Instala el compilador si no está
install_solc('0.8.0')

# Conecta a Ganache (corre primero Ganache local)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
w3.eth.default_account = w3.eth.accounts[0]

# Carga el código del contrato
with open("app/contracts/CheckpointContract.sol", "r") as f:
    source_code = f.read()

# Compila
compiled = compile_source(source_code, solc_version="0.8.0")
contract_id, contract_interface = compiled.popitem()

# Prepara contrato
abi = contract_interface["abi"]
bytecode = contract_interface["bin"]
CheckpointContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Despliega
tx_hash = CheckpointContract.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contrato desplegado en:", tx_receipt.contractAddress)

# Guarda ABI y dirección para usar luego en Flask
with open("contracts/compiled_contract.json", "w") as f:
    json.dump({
        "abi": abi,
        "address": tx_receipt.contractAddress
    }, f, indent=4)
