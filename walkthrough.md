# JWT Authentication Service Walkthrough (Permission-Based RBAC)

I have successfully implemented **Permission-Based RBAC** with resource-based permission naming for clarity and maintainability.

## Changes Implemented

### 1. Resource-Based Permission Naming
- **`auth_service/permissions.json`**: Defines role-to-permission mappings using resource-based names
  - `read:data` - Access to general data resources
  - `read:admin_panel` - Access to admin panel resources
  - `write:admin_panel` - Modify admin panel resources
  - `delete:users` - Delete user resources

### 2. Permission-Based RBAC Architecture
- **Auth Service**: 
  - Loads `permissions.json` at startup
  - Resolves permissions from user roles
  - Embeds `permissions` array in JWT payload
- **Resource Service**:
  - Extracts `permissions` from JWT
  - Uses `@permission_required('resource:action')` decorator
  - No API calls needed - all validation is local

### 3. Endpoint Protection
- `/protected` - Requires `read:data` permission
- `/admin` - Requires `read:admin_panel` permission  
- `/admin/users` (DELETE) - Requires `delete:users` permission

### 4. Key Features
- **Stateless**: Permissions in JWT, no database lookups
- **Scalable**: No external RBAC service calls
- **Flexible**: Add new roles/permissions in `permissions.json` without code changes
- **Clear**: Resource-based naming (not URL-based)

## File Organization
- `auth_service/secrets.json` - User credentials
- `auth_service/permissions.json` - Role-permission mappings
- `keys/` - RSA key pairs
- `config.json` - Shared configuration

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
    python test/verify_flow.py
    ```
