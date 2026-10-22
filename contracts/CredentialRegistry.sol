
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CredentialRegistry {
    struct Credential {
        string credentialId;
        bytes32 certificateHash;
        string studentId;
        string studentName;
        string degree;
        string institution;
        uint256 issueDate;
        bool revoked;
        address issuer;
    }

    mapping(string => Credential) private credentials;

    event CredentialIssued(
        string credentialId,
        bytes32 certificateHash,
        string studentId,
        address issuer
    );

    event CredentialRevoked(
        string credentialId,
        address issuer
    );

    function issueCredential(
        string memory _credentialId,
        bytes32 _certificateHash,
        string memory _studentId,
        string memory _studentName,
        string memory _degree,
        string memory _institution
    ) public {
        require(
            credentials[_credentialId].issueDate == 0,
            "Credential already exists"
        );

        credentials[_credentialId] = Credential({
            credentialId: _credentialId,
            certificateHash: _certificateHash,
            studentId: _studentId,
            studentName: _studentName,
            degree: _degree,
            institution: _institution,
            issueDate: block.timestamp,
            revoked: false,
            issuer: msg.sender
        });

        emit CredentialIssued(
            _credentialId,
            _certificateHash,
            _studentId,
            msg.sender
        );
    }

    function revokeCredential(string memory _credentialId) public {
        require(
            credentials[_credentialId].issueDate != 0,
            "Credential does not exist"
        );
        require(
            credentials[_credentialId].issuer == msg.sender,
            "Only issuer can revoke"
        );
        require(
            !credentials[_credentialId].revoked,
            "Credential already revoked"
        );

        credentials[_credentialId].revoked = true;
        emit CredentialRevoked(_credentialId, msg.sender);
    }

    function getCredential(
        string memory _credentialId
    ) public view returns (
        string memory,
        bytes32,
        string memory,
        string memory,
        string memory,
        string memory,
        uint256,
        bool,
        address
    ) {
        require(
            credentials[_credentialId].issueDate != 0,
            "Credential does not exist"
        );

        Credential memory c = credentials[_credentialId];

        return (
            c.credentialId,
            c.certificateHash,
            c.studentId,
            c.studentName,
            c.degree,
            c.institution,
            c.issueDate,
            c.revoked,
            c.issuer
        );
    }
    function verifyCredential(
    string memory _credentialId,
    bytes32 _certificateHash
)
    public
    view
    returns (
        bool isValid,
        bool isRevoked,
        string memory studentName,
        string memory degree,
        string memory institution,
        string memory studentId,
        uint256 issueDate,
        address issuer
    )
{
    Credential storage c = credentials[_credentialId];

    if (c.issueDate == 0) {
        return (
            false,
            false,
            "",
            "",
            "",
            "",
            0,
            address(0)
        );
    }

    bool hashMatches = c.certificateHash == _certificateHash;

    return (
        hashMatches && !c.revoked,
        c.revoked,
        c.studentName,
        c.degree,
        c.institution,
        c.studentId,
        c.issueDate,
        c.issuer
    );
}
}
