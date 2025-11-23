import requests
import json
import time

# Load Config
with open('config.json', 'r') as f:
    config = json.load(f)

AUTH_SERVICE_URL = config['auth_service_url']
RESOURCE_SERVICE_URL = config['resource_service_url']

def run_verification():
    print("--- Starting Verification Flow (File-Based Keys) ---")

    # 1. Login
    print("\n1. Logging in as 'user1'...")
    login_payload = {"username": "user1", "password": "password123"}
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=login_payload)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            print(f"SUCCESS: Login successful.")
        else:
            print(f"FAILED: Login failed. {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("FAILED: Could not connect to Auth Service.")
        return

    # 2. Access Protected Resource
    print("\n2. Accessing Protected Resource (Token A)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers)
    if response.status_code == 200:
        print(f"SUCCESS: Accessed protected resource.")
        print(f"Data: {response.json().get('data')}")
    else:
        print(f"FAILED: Access denied. {response.text}")

    # 3. Refresh Token
    print("\n3. Refreshing Access Token...")
    refresh_payload = {"refresh_token": refresh_token}
    response = requests.post(f"{AUTH_SERVICE_URL}/refresh", json=refresh_payload)
    if response.status_code == 200:
        new_access_token = response.json()['access_token']
        print(f"SUCCESS: Token refreshed.")
    else:
        print(f"FAILED: Refresh failed. {response.text}")
        return

    # 4. Access Protected Resource with New Token
    print("\n4. Accessing Protected Resource (Token B)...")
    headers_new = {"Authorization": f"Bearer {new_access_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers_new)
    if response.status_code == 200:
        print(f"SUCCESS: Accessed protected resource with NEW token.")
    else:
        print(f"FAILED: Access denied with new token. {response.text}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
