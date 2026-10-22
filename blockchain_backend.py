
import json
import hashlib
from pathlib import Path

from web3 import Web3


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

with open(
    BASE_DIR / "contract_config.json",
    encoding="utf-8",
) as f:
    CONFIG = json.load(f)

with open(
    BASE_DIR / "contract_abi.json",
    encoding="utf-8",
) as f:
    ABI = json.load(f)


# --------------------------------------------------
# BLOCKCHAIN CONNECTION
# --------------------------------------------------

w3 = Web3(
    Web3.HTTPProvider(CONFIG["rpc_url"])
)

if not w3.is_connected():
    raise ConnectionError(
        "Cannot connect to Ganache. Start the blockchain first."
    )

if w3.eth.chain_id != CONFIG["chain_id"]:
    raise RuntimeError(
        "Connected to the wrong blockchain."
    )

issuer_account = Web3.to_checksum_address(
    CONFIG["issuer_account"]
)

contract_address = Web3.to_checksum_address(
    CONFIG["contract_address"]
)

if not w3.eth.get_code(contract_address):
    raise RuntimeError(
        "Contract not found at saved address. "
        "Check Ganache and contract_config.json."
    )

contract = w3.eth.contract(
    address=contract_address,
    abi=ABI,
)


# --------------------------------------------------
# PDF HASHING
# --------------------------------------------------

def calculate_pdf_hash(pdf_bytes: bytes) -> str:
    """Return the SHA-256 hash of the exact PDF bytes."""
    return hashlib.sha256(pdf_bytes).hexdigest()


# --------------------------------------------------
# BLOCKCHAIN STATUS
# --------------------------------------------------

def get_blockchain_status() -> dict:
    """Return the current blockchain connection details."""
    return {
        "connected": w3.is_connected(),
        "chain_id": w3.eth.chain_id,
        "latest_block": w3.eth.block_number,
        "contract_address": contract_address,
        "issuer_account": issuer_account,
    }


# --------------------------------------------------
# GET CREDENTIAL
# --------------------------------------------------

def get_credential(credential_id: str):
    """
    Return the on-chain credential tuple.
    Return None if the credential does not exist.
    """
    try:
        return contract.functions.getCredential(
            credential_id
        ).call({"from": issuer_account})

    except Exception as exc:
        if "Credential does not exist" in str(exc):
            return None
        raise


# --------------------------------------------------
# ISSUE CREDENTIAL
# --------------------------------------------------

def issue_credential(
    credential_id: str,
    student_id: str,
    student_name: str,
    degree: str,
    institution: str,
    pdf_bytes: bytes,
) -> dict:
    """Hash a PDF and issue its credential on the blockchain."""

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError(
            "Please upload a valid PDF certificate."
        )

    if get_credential(credential_id) is not None:
        raise ValueError(
            "This credential ID already exists."
        )

    pdf_hash = calculate_pdf_hash(pdf_bytes)
    hash_bytes = bytes.fromhex(pdf_hash)

    tx_hash = contract.functions.issueCredential(
        credential_id,
        hash_bytes,
        student_id,
        student_name,
        degree,
        institution,
    ).transact({
        "from": issuer_account,
        "gas": 500_000,
    })

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    if receipt.status != 1:
        raise RuntimeError(
            "Credential transaction failed."
        )

    return {
        "credential_id": credential_id,
        "certificate_hash": pdf_hash,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
    }


# --------------------------------------------------
# REVOKE CREDENTIAL
# --------------------------------------------------

def revoke_credential(credential_id: str) -> dict:
    """Revoke a credential issued by the current account."""

    record = get_credential(credential_id)

    if record is None:
        raise ValueError(
            "Credential does not exist."
        )

    if record[7]:
        raise ValueError(
            "Credential is already revoked."
        )

    # Only the original issuer can revoke this credential.
    if record[8].lower() != issuer_account.lower():
        raise PermissionError(
            "This account did not issue the credential."
        )

    tx_hash = contract.functions.revokeCredential(
        credential_id
    ).transact({
        "from": issuer_account,
        "gas": 300_000,
    })

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    if receipt.status != 1:
        raise RuntimeError(
            "Revocation transaction failed."
        )

    return {
        "credential_id": credential_id,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "revoked": True,
    }


# --------------------------------------------------
# VERIFY CREDENTIAL
# --------------------------------------------------

def verify_credential(
    credential_id: str,
    pdf_bytes: bytes,
) -> dict:
    """
    Verify the PDF hash against the blockchain record,
    using Solidity verifyCredential() and checking revocation.
    """

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError(
            "Please upload a valid PDF certificate."
        )

    # First check whether the credential exists.
    record = get_credential(credential_id)

    if record is None:
        return {
            "exists": False,
            "valid": False,
            "revoked": False,
            "hash_matches": False,
            "message": "Credential does not exist.",
        }

    pdf_hash = calculate_pdf_hash(pdf_bytes)
    hash_bytes = bytes.fromhex(pdf_hash)

    # Verify the hash and revocation status on-chain.
    result = contract.functions.verifyCredential(
        credential_id,
        hash_bytes,
    ).call({"from": issuer_account})

    (
        is_valid,
        is_revoked,
        student_name,
        degree,
        institution,
        student_id,
        issue_date,
        issuer,
    ) = result

    # Convert the stored bytes32 hash to a comparable hex string.
    stored_hash = (
        record[1].hex()
        if isinstance(record[1], bytes)
        else str(record[1]).removeprefix("0x")
    )

    hash_matches = (
        stored_hash.lower() == pdf_hash.lower()
    )

    # Determine the result message.
    if is_revoked:
        message = "Credential has been revoked."
    elif not hash_matches:
        message = (
            "Certificate hash does not match "
            "the blockchain record."
        )
    elif is_valid and hash_matches:
        message = "Certificate verified successfully."
    else:
        message = "Certificate is not valid."

    return {
        "exists": True,
        "valid": bool(
            is_valid and hash_matches and not is_revoked
        ),
        "revoked": bool(is_revoked),
        "hash_matches": hash_matches,
        "credential_id": record[0],
        "certificate_hash": pdf_hash,
        "student_id": student_id,
        "student_name": student_name,
        "degree": degree,
        "institution": institution,
        "issue_date": issue_date,
        "issuer": issuer,
        "message": message,
    }
