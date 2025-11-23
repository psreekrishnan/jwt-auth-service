import jwt
import datetime
import json
import os
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Load Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
SECRETS_PATH = os.path.join(SERVICE_DIR, 'secrets.json')
PERMISSIONS_PATH = os.path.join(SERVICE_DIR, 'permissions.json')
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'keys', 'private_key.pem')

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

with open(SECRETS_PATH, 'r') as f:
    secrets = json.load(f)

with open(PERMISSIONS_PATH, 'r') as f:
    permissions_config = json.load(f)

# Load Private Key
with open(PRIVATE_KEY_PATH, 'rb') as f:
    PRIVATE_KEY = f.read()

users = secrets['users']
ACCESS_TOKEN_EXPIRATION_MINUTES = config['access_token_expiration_minutes']
REFRESH_TOKEN_EXPIRATION_DAYS = config['refresh_token_expiration_days']

# Mock Refresh Token Store
refresh_tokens = {}

def get_permissions_for_roles(roles):
    """
    Resolve permissions from roles using permissions.json
    Returns a unique list of permissions
    """
    permissions = set()
    for role in roles:
        if role in permissions_config['roles']:
            role_permissions = permissions_config['roles'][role]['permissions']
            permissions.update(role_permissions)
    return list(permissions)

def generate_access_token(username, roles):
    # Get permissions for the user's roles
    permissions = get_permissions_for_roles(roles)
    
    payload = {
        'sub': username,
        'roles': roles,
        'permissions': permissions,  # NEW: Embed permissions in JWT
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    
    # Sign with RS256 using the loaded Private Key
    token = jwt.encode(
        payload, 
        PRIVATE_KEY, 
        algorithm='RS256'
    )
    return token

def generate_refresh_token(username):
    # Static secret for refresh tokens
    payload = {
        'sub': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, "REFRESH_SECRET_KEY_STATIC", algorithm='HS256')

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    username = auth.get('username')
    password = auth.get('password')

    if username in users:
        user_data = users[username]
        stored_password = user_data['password']
        
        if stored_password == password:
            roles = user_data.get('roles', [])
            access_token = generate_access_token(username, roles)
            refresh_token = generate_refresh_token(username)
            
            refresh_tokens[refresh_token] = username
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token
            })

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/refresh', methods=['POST'])
def refresh():
    data = request.json
    if not data or not data.get('refresh_token'):
        return jsonify({'message': 'Refresh token is missing!'}), 400
    
    token = data.get('refresh_token')
    
    try:
        payload = jwt.decode(token, "REFRESH_SECRET_KEY_STATIC", algorithms=['HS256'])
        if payload['type'] != 'refresh':
             return jsonify({'message': 'Invalid token type!'}), 401
             
        username = payload['sub']
        
        if token not in refresh_tokens or refresh_tokens[token] != username:
             return jsonify({'message': 'Invalid or revoked refresh token!'}), 401

        # Fetch roles and permissions again for the new token
        roles = users[username]['roles']
        new_access_token = generate_access_token(username, roles)
        
        return jsonify({'access_token': new_access_token})
        
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token!'}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)
