import requests
import json
import os

# Load Config from parent directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

AUTH_SERVICE_URL = config['auth_service_url']
RESOURCE_SERVICE_URL = config['resource_service_url']

def run_verification():
    print("--- Starting Verification Flow (Permission-Based RBAC) ---")

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

    # 2. Access Protected Resource (User - has 'read:protected' permission)
    print("\n2. User accessing /protected...")
    headers_user = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers_user)
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: User accessed protected resource.")
        print(f"  Permissions: {data.get('permissions')}")
    else:
        print(f"FAILED: {response.text}")

    # 3. User trying to access Admin Resource (lacks 'read:admin_panel' permission)
    print("\n3. User trying to access /admin (Should FAIL - lacks 'read:admin_panel')...")
    response = requests.get(f"{RESOURCE_SERVICE_URL}/admin", headers=headers_user)
    if response.status_code == 403:
        data = response.json()
        print(f"SUCCESS: Access denied as expected.")
        print(f"  Message: {data.get('message')}")
    else:
        print(f"FAILED: User accessed admin resource! Status: {response.status_code}")

    # 4. User trying to delete users (lacks 'delete:users' permission)
    print("\n4. User trying to DELETE /admin/users (Should FAIL - lacks 'delete:users')...")
    response = requests.delete(f"{RESOURCE_SERVICE_URL}/admin/users", headers=headers_user)
    if response.status_code == 403:
        print(f"SUCCESS: Access denied as expected.")
    else:
        print(f"FAILED: User accessed delete endpoint! Status: {response.status_code}")

    # 5. Refresh Token (User)
    print("\n5. Refreshing User Access Token...")
    refresh_payload = {"refresh_token": user_refresh_token}
    response = requests.post(f"{AUTH_SERVICE_URL}/refresh", json=refresh_payload)
    if response.status_code == 200:
        new_user_token = response.json()['access_token']
        print(f"SUCCESS: Token refreshed.")
    else:
        print(f"FAILED: Refresh failed. {response.text}")
        return

    # 6. Access Protected Resource with New Token
    print("\n6. User accessing /protected with NEW token...")
    headers_new = {"Authorization": f"Bearer {new_user_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/protected", headers=headers_new)
    if response.status_code == 200:
        print(f"SUCCESS: User accessed protected resource with NEW token.")
    else:
        print(f"FAILED: Access denied with new token. {response.text}")

    # 7. Login as Admin
    print("\n7. Logging in as 'admin' (Role: admin)...")
    login_payload_admin = {"username": "admin", "password": "adminpassword"}
    response = requests.post(f"{AUTH_SERVICE_URL}/login", json=login_payload_admin)
    tokens = response.json()
    admin_token = tokens['access_token']
    print(f"SUCCESS: Got Admin Token.")

    # 8. Admin accessing Admin Resource (has 'read:admin' permission)
    print("\n8. Admin accessing /admin...")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{RESOURCE_SERVICE_URL}/admin", headers=headers_admin)
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Admin accessed admin resource.")
        print(f"  Permissions: {data.get('permissions')}")
    else:
        print(f"FAILED: Admin denied access! {response.text}")

    # 9. Admin deleting users (has 'delete:users' permission)
    print("\n9. Admin accessing DELETE /admin/users...")
    response = requests.delete(f"{RESOURCE_SERVICE_URL}/admin/users", headers=headers_admin)
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Admin accessed delete endpoint.")
        print(f"  Message: {data.get('message')}")
    else:
        print(f"FAILED: Admin denied access! {response.text}")

    print("\n--- Verification Complete ---")
    print("\nKey Takeaways:")
    print("* Permissions are embedded in JWT (no API calls needed)")
    print("* Resource-based permissions (read:data, read:admin_panel, delete:users)")
    print("* User with 'user' role can only read:data")
    print("* Admin with 'admin' role has all permissions")

if __name__ == "__main__":
    run_verification()
