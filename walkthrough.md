# JWT Authentication Service Walkthrough (File-Based Keys)

I have successfully refactored the service to use **File-Based Key Distribution** and verified the full **Login -> Access -> Refresh -> Access** flow.

## Changes Implemented

### 1. Key Generation
- **`key_generator.py`**: A standalone script that generates an RSA 2048 Key Pair.
- **Output**: Saves `private_key.pem` and `public_key.pem` to the `keys/` directory.

### 2. Auth Service
- Loads `keys/private_key.pem` on startup.
- Signs tokens using this private key (RS256).
- Implements `/refresh` endpoint to issue new access tokens.

### 3. Resource Service
- Loads `keys/public_key.pem` on startup.
- Verifies tokens using this public key.

## Verification Results

I ran the `verify_flow.py` script which now tests the complete lifecycle:

```text
--- Starting Verification Flow (File-Based Keys) ---

1. Logging in as 'user1'...
SUCCESS: Login successful.

2. Accessing Protected Resource (Token A)...
SUCCESS: Accessed protected resource.
Data: [1, 2, 3, 4, 5]

3. Refreshing Access Token...
SUCCESS: Token refreshed.

4. Accessing Protected Resource (Token B)...
SUCCESS: Accessed protected resource with NEW token.

--- Verification Complete ---
```

## How to Run

1.  **Generate Keys**:
    ```bash
    python key_generator.py
    ```
2.  **Start Auth Service**:
    ```bash
    python auth_service/main.py
    ```
3.  **Start Resource Service**:
    ```bash
    python resource_service/main.py
    ```
4.  **Run Verification**:
    ```bash
    python verify_flow.py
    ```
