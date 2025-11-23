import requests
import json

# Load Config
with open('config.json', 'r') as f:
    config = json.load(f)

AUTH_SERVICE_URL = config['auth_service_url']
RESOURCE_SERVICE_URL = config['resource_service_url']

def run_verification():
    print("--- Starting Verification Flow (RBAC + Refresh) ---")

    # 1. Login as Regular User
    print("\n1. Logging in as 'user1' (Role: user)...")
    login_payload = {"username": "user1", "password": "password123"}
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=login_payload)
        tokens = response.json()
        user_token = tokens['access_token']
        user_refresh_token = tokens['refresh_token']
        print(f"SUCCESS: Got User Token.")
    except Exception as e:
        print(f"FAILED: {e}")
        return

    # 2. Access Protected Resource (User)
    print("\n2. User accessing /protected...")
    headers_user = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers_user)
    if response.status_code == 200:
        print(f"SUCCESS: User accessed protected resource. Roles: {response.json().get('roles')}")
    else:
        print(f"FAILED: {response.text}")

    # 3. User trying to access Admin Resource
    print("\n3. User trying to access /admin (Should FAIL)...")
    response = requests.get(f"{RESOURCE_SERVICE_URL}/admin", headers=headers_user)
    if response.status_code == 403:
        print(f"SUCCESS: Access denied as expected. {response.json().get('message')}")
    else:
        print(f"FAILED: User accessed admin resource! Status: {response.status_code}")

    # 4. Refresh Token (User)
    print("\n4. Refreshing User Access Token...")
    refresh_payload = {"refresh_token": user_refresh_token}
    response = requests.post(f"{AUTH_SERVICE_URL}/refresh", json=refresh_payload)
    if response.status_code == 200:
        new_user_token = response.json()['access_token']
        print(f"SUCCESS: Token refreshed.")
    else:
        print(f"FAILED: Refresh failed. {response.text}")
        return

    # 5. Access Protected Resource with New Token
    print("\n5. User accessing /protected with NEW token...")
    headers_new = {"Authorization": f"Bearer {new_user_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers_new)
    if response.status_code == 200:
        print(f"SUCCESS: User accessed protected resource with NEW token.")
    else:
        print(f"FAILED: Access denied with new token. {response.text}")

    # 6. Login as Admin
    print("\n6. Logging in as 'admin' (Role: admin)...")
    login_payload_admin = {"username": "admin", "password": "adminpassword"}
    response = requests.post(f"{AUTH_SERVICE_URL}/login", json=login_payload_admin)
    admin_token = response.json()['access_token']
    print(f"SUCCESS: Got Admin Token.")

    # 7. Admin accessing Admin Resource
    print("\n7. Admin accessing /admin...")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/admin", headers=headers_admin)
    if response.status_code == 200:
        print(f"SUCCESS: Admin accessed admin resource. Message: {response.json().get('message')}")
    else:
        print(f"FAILED: Admin denied access! {response.text}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
