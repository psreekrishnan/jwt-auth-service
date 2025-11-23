# JWT Authentication Service

## Project Structure

- `auth_service/`: Contains the Authentication Service code
  - `main.py`: Auth service implementation
  - `secrets.json`: User credentials (not committed to git)
  - `permissions.json`: Role-to-permission mappings
  - `requirements.txt`: Python dependencies
- `resource_service/`: Contains the Resource Service code
  - `main.py`: Resource service implementation
  - `requirements.txt`: Python dependencies
- `test/`: Contains verification scripts
  - `verify_flow.py`: End-to-end verification script
- `keys/`: Contains the generated RSA keys (not committed to git)
  - `private_key.pem`: Private key for signing tokens
  - `public_key.pem`: Public key for verifying tokens
- `key_generator.py`: Script to generate new RSA key pairs
- `config.json`: Shared configuration (token expiry, service URLs)
- `architecture.md`: Detailed architecture and flow documentation
- `flow.puml`: PlantUML sequence diagram
- `walkthrough.md`: Verification results

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r auth_service/requirements.txt
    pip install -r resource_service/requirements.txt
    ```

2.  **Generate Keys**:
    Run this once to create the `keys/` directory and generate the key pair.
    ```bash
    python key_generator.py
    ```

## Running the Services

1.  **Start Auth Service** (Port 5000):
    ```bash
    python auth_service/main.py
    ```

2.  **Start Resource Service** (Port 5001):
    ```bash
    python resource_service/main.py
    ```

## Verification

Once both services are running, you can run the verification script:

```bash
python test/verify_flow.py
```

## Manual Testing (cURL)

### 1. Login
```bash
curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d "{\"username\": \"user1\", \"password\": \"password123\"}"
```

### 2. Access Protected Resource
```bash
curl -X GET http://localhost:5001/protected \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 3. Access Admin Resource
```bash
curl -X GET http://localhost:5001/admin \
     -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>"
```

### 4. Delete Users (Admin only)
```bash
curl -X DELETE http://localhost:5001/admin/users \
     -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>"
```
