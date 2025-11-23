# JWT Authentication Service

## Project Structure

- `auth_service/`: Contains the Authentication Service code.
- `resource_service/`: Contains the Resource Service code.
- `test/`: Contains verification scripts.
- `keys/`: Contains the generated RSA keys (`private_key.pem`, `public_key.pem`).
- `key_generator.py`: Script to generate new keys.
- `config.json`: Shared configuration.
- `secrets.json`: User credentials.
- `architecture.md`: Detailed architecture and flow documentation.
- `flow.puml`: PlantUML sequence diagram.
- `walkthrough.md`: Verification results.

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
