
import json
from pathlib import Path
from solcx import compile_source, set_solc_version

# Project paths
BASE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = BASE_DIR / "contracts" / "CredentialRegistry.sol"

# Load Solidity source
source = CONTRACT_PATH.read_text(encoding="utf-8")

# Compile using Solidity 0.8.20
set_solc_version("0.8.20")

compiled = compile_source(
    source,
    output_values=["abi", "bin"]
)

# Get compiled contract
contract_id, contract_interface = next(iter(compiled.items()))

# Save ABI
(BASE_DIR / "contract_abi.json").write_text(
    json.dumps(contract_interface["abi"], indent=2),
    encoding="utf-8"
)

# Save bytecode
(BASE_DIR / "contract_bytecode.txt").write_text(
    contract_interface["bin"],
    encoding="utf-8"
)

print("Compilation successful!")
print("Contract:", contract_id)
print("ABI saved to contract_abi.json")
print("Bytecode saved to contract_bytecode.txt")
