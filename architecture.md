# JWT Authentication Architecture & Flow (File-Based Keys)

This document explains the architecture of the JWT Authentication service, using **File-Based Asymmetric Keys**.

## Architecture Overview

1.  **Key Generation**:
    *   `key_generator.py` creates an RSA 2048 Key Pair.
    *   Saves `private_key.pem` and `public_key.pem` to the `keys/` directory.

2.  **Auth Service (Port 5000)**:
    *   **Startup**: Loads `keys/private_key.pem`.
    *   **Login**: Signs tokens using the loaded **Private Key**.
    *   **Refresh**: Validates Refresh Token (HS256) and issues new Access Token (RS256).

3.  **Resource Service (Port 5001)**:
    *   **Startup**: Loads `keys/public_key.pem`.
    *   **Validation**: Verifies tokens using the loaded **Public Key**.

## Application Flow

The sequence diagram is available in **[flow.puml](flow.puml)**.

It covers:
1.  **Startup**: Loading keys from file system.
2.  **Login**: Getting Access & Refresh Tokens.
3.  **Access**: Accessing protected resources.
4.  **Refresh**: Getting a new Access Token using a Refresh Token.

## Key Concepts

### 1. Asymmetric Keys (RS256)
*   **Auth Service** has the **Private Key** (can create tokens).
*   **Resource Service** has the **Public Key** (can only verify).

### 2. Key Rotation
*   Rotation is **Manual**.
*   To rotate keys:
    1.  Run `python key_generator.py` (Overwrites old keys).
    2.  Restart Auth Service.
    3.  Restart Resource Service.
