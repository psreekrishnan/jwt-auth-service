# JWT Authentication Architecture & Flow (File-Based Keys + RBAC)

This document explains the architecture of the JWT Authentication service, using **File-Based Asymmetric Keys** and **Role-Based Access Control (RBAC)**.

## Architecture Overview

1.  **Key Generation**:
    *   `key_generator.py` creates an RSA 2048 Key Pair.
    *   Saves `private_key.pem` and `public_key.pem` to the `keys/` directory.

2.  **Auth Service (Port 5000)**:
    *   **Startup**: Loads `keys/private_key.pem`.
    *   **Login**: Authenticates user, reads roles from `secrets.json`, and includes them in the JWT.
    *   **Refresh**: Validates Refresh Token and issues new Access Token with roles.

3.  **Resource Service (Port 5001)**:
    *   **Startup**: Loads `keys/public_key.pem`.
    *   **Validation**: Verifies tokens using the loaded **Public Key**.
    *   **RBAC**: Enforces role requirements using `@role_required` decorator.

## Application Flow

### Mermaid Diagram

```mermaid
sequenceDiagram
    participant Client
    participant Auth as Auth Service
    participant Resource as Resource Service
    participant FS as File System

    Note over Auth, Resource: 1. Startup
    Auth->>FS: Load private_key.pem
    Resource->>FS: Load public_key.pem

    Note over Client, Auth: 2. Login Flow
    Client->>Auth: POST /login (username, password)
    Auth->>Auth: Validate User & Roles
    Auth->>Auth: Sign Access Token (RS256) with Roles
    Auth-->>Client: Returns {access_token, refresh_token}

    Note over Client, Resource: 3. Access Protected Resource (User Role)
    Client->>Resource: GET /protected (Header: Bearer <token>)
    Resource->>Resource: Verify Signature (Public Key)
    Resource->>Resource: Check Role (User)
    Resource-->>Client: Returns 200 OK + Data

    Note over Client, Resource: 4. Access Admin Resource (Admin Role)
    Client->>Resource: GET /admin (Header: Bearer <token>)
    Resource->>Resource: Verify Signature & Check Role (Admin)
    alt Role == Admin
        Resource-->>Client: Returns 200 OK + Admin Data
    else Role != Admin
        Resource-->>Client: Returns 403 Forbidden
    end

    Note over Client, Auth: 5. Refresh Flow
    Client->>Auth: POST /refresh (refresh_token)
    Auth->>Auth: Verify Refresh Token
    Auth->>Auth: Issue NEW Access Token
    Auth-->>Client: Returns {access_token}
```

### Detailed PlantUML

For a more detailed view, see **[flow.puml](flow.puml)**.

## Key Concepts

### 1. Asymmetric Keys (RS256)
*   **Auth Service** has the **Private Key** (can create tokens).
*   **Resource Service** has the **Public Key** (can only verify).

### 2. Role-Based Access Control (RBAC)
*   **Roles**: Defined in `secrets.json` (e.g., `admin`, `user`).
*   **Claims**: Roles are embedded in the JWT payload (`"roles": ["admin"]`).
*   **Enforcement**: Resource Service checks the `roles` claim before allowing access to protected endpoints.
