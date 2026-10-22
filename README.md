# Academic Credential Verification

A local demonstration app for issuing, verifying, and revoking academic
credentials using a Solidity contract, a Ganache development blockchain, and
Streamlit.

## Requirements

- Node.js and npm
- Python 3.10 or newer

## Setup and run

From the project directory:

```bash
npm ci
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start Ganache in one terminal:

```bash
npm exec ganache -- --server.host 127.0.0.1 --server.port 8545 --chain.chainId 1337 --database.dbPath ./chain-data
```

In a second terminal, activate the virtual environment and compile and deploy
the contract:

```bash
source .venv/bin/activate
python compile_contract.py
python deploy_contract.py
```

Deployment creates `contract_config.json` locally. Start the app:

```bash
streamlit run app/app.py
```

Open the local URL printed by Streamlit (normally
`http://localhost:8501`). To check the backend connection, run
`python test_backend.py` after Ganache and deployment are running.

## Privacy and deployment

This project is a local prototype, not a production credential system. The
contract stores student details on-chain in readable form. Use fictional test
data only, and do not deploy this contract to a public blockchain or upload
real credentials or student records. Local blockchain state, deployment
configuration, generated certificates, and QR images are intentionally
excluded from Git.
