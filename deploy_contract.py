
import json
from pathlib import Path
from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent

# Connect to Ganache
w3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:8545")
)

if not w3.is_connected():
    raise ConnectionError(
        "Ganache is not running. Start Ganache first."
    )

# Load compiled contract
abi = json.loads(
    (BASE_DIR / "contract_abi.json").read_text()
)

bytecode = (
    BASE_DIR / "contract_bytecode.txt"
).read_text().strip()

# Use first Ganache account as issuer
issuer = w3.eth.accounts[0]
w3.eth.default_account = issuer

# Create contract factory
CredentialRegistry = w3.eth.contract(
    abi=abi,
    bytecode=bytecode
)

# Deploy contract
tx_hash = CredentialRegistry.constructor().transact({
    "from": issuer,
    "gas": 5_000_000
})

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

if receipt.status != 1:
    raise RuntimeError("Contract deployment failed.")

contract_address = receipt.contractAddress

# Save deployment configuration
config = {
    "rpc_url": "http://127.0.0.1:8545",
    "chain_id": w3.eth.chain_id,
    "contract_address": contract_address,
    "issuer_account": issuer,
    "deployment_block": receipt.blockNumber
}

(BASE_DIR / "contract_config.json").write_text(
    json.dumps(config, indent=2)
)

# Verify deployed bytecode exists
code = w3.eth.get_code(contract_address)

if len(code) == 0:
    raise RuntimeError(
        "Deployment address has no contract code."
    )

print("Contract deployed successfully!")
print("Chain ID:", w3.eth.chain_id)
print("Issuer:", issuer)
print("Contract address:", contract_address)
print("Deployment block:", receipt.blockNumber)
print("Contract code verified:", len(code) > 0)
print("Configuration saved to contract_config.json")
