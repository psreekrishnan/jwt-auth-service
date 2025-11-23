import jwt
import datetime
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class KeyManager:
    def __init__(self, overlap_minutes=20):
        self.keys = {} # Map of kid -> {private_key, public_key, created_at, expires_at}
        self.current_kid = None
        self.overlap_minutes = overlap_minutes
        self.rotate() # Generate initial key

    def generate_key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        kid = f"key-{int(datetime.datetime.utcnow().timestamp())}"
        
        # Convert public key to PEM format for storage/display
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return kid, private_key, pem_public

    def rotate(self):
        # Generate new key
        new_kid, new_private, new_public = self.generate_key()
        
        now = datetime.datetime.utcnow()
        
        # Add new key
        self.keys[new_kid] = {
            "private_key": new_private,
            "public_key": new_public,
            "created_at": now,
            "expires_at": None # Active key doesn't have expiry yet
        }
        
        # Mark old key for expiration (Overlap Period)
        if self.current_kid:
            old_key = self.keys[self.current_kid]
            old_key["expires_at"] = now + datetime.timedelta(minutes=self.overlap_minutes)
            
        self.current_kid = new_kid
        
        # Cleanup expired keys
        self.cleanup()
        
        return new_kid

    def cleanup(self):
        now = datetime.datetime.utcnow()
        keys_to_remove = []
        for kid, key_data in self.keys.items():
            if key_data["expires_at"] and key_data["expires_at"] < now:
                keys_to_remove.append(kid)
        
        for kid in keys_to_remove:
            del self.keys[kid]

    def get_current_key(self):
        return self.keys[self.current_kid]["private_key"], self.current_kid

    def get_jwks(self):
        self.cleanup() # Ensure we don't serve expired keys
        keys_list = []
        for kid, key_data in self.keys.items():
            # Note: In a real JWKS, you'd break down the RSA key into n and e components.
            # For simplicity with PyJWT, we can serve the PEM or use jwt.algorithms.RSAAlgorithm
            # But standard JWKS uses 'n' and 'e'. 
            # To keep this demo simple and compatible with PyJWT's easy loading, 
            # we will just embed the PEM in a custom field or rely on PyJWT to handle PEM if we pass it.
            # However, standard JWKS requires 'n' and 'e'. Let's do it properly.
            
            public_key = key_data["public_key"] # This is PEM
            # We can use PyJWT to convert PEM to JWK format if needed, or just serve PEM.
            # Most libraries expect standard JWKS.
            # Let's use a helper to convert RSA public key to JWK params.
            
            # For this demo, we will return a simplified JWKS-like structure that PyJWT can parse 
            # if we write a smart client, OR we just return the PEMs mapped by KID.
            # Let's stick to standard JWKS structure as much as possible.
            
            # Extract numbers
            priv = key_data["private_key"]
            pub = priv.public_key()
            pub_nums = pub.public_numbers()
            
            # Base64URL encode (helper function needed)
            def to_base64url_uint(val):
                import base64
                bytes_val = val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')
                return base64.urlsafe_b64encode(bytes_val).decode('utf-8').rstrip('=')

            keys_list.append({
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": to_base64url_uint(pub_nums.n),
                "e": to_base64url_uint(pub_nums.e)
            })
            
        return {"keys": keys_list}
