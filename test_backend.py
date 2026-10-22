
import blockchain_backend as backend

status = backend.get_blockchain_status()

print("Blockchain connected:", status["connected"])
print("Chain ID:", status["chain_id"])
print("Latest block:", status["latest_block"])
print("Contract address:", status["contract_address"])
print("Issuer account:", status["issuer_account"])
print("Backend loaded successfully!")
