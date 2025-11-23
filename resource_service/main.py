import jwt
import json
import os
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Load Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'keys', 'public_key.pem')

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

# Load Public Key
with open(PUBLIC_KEY_PATH, 'rb') as f:
    PUBLIC_KEY = f.read()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format invalid!'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Verify Signature using the loaded Public Key
            data = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
            
            if data['type'] != 'access':
                 return jsonify({'message': 'Invalid token type! Expected access token.'}), 401
            
            current_user = data['sub']
            current_roles = data.get('roles', [])
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401
            
        # Pass user and roles to the route
        return f(current_user, current_roles, *args, **kwargs)
    
    return decorated

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, current_roles, *args, **kwargs):
            if required_role not in current_roles:
                return jsonify({'message': f'Access denied! Required role: {required_role}'}), 403
            return f(current_user, current_roles, *args, **kwargs)
        return decorated_function
    return decorator

@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user, current_roles):
    return jsonify({
        'message': 'This is a protected resource.',
        'user': current_user,
        'roles': current_roles,
        'data': [1, 2, 3, 4, 5]
    })

@app.route('/admin', methods=['GET'])
@token_required
@role_required('admin')
def admin_only(current_user, current_roles):
    return jsonify({
        'message': 'Welcome Admin!',
        'user': current_user,
        'secret_admin_data': 'TOP SECRET'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
