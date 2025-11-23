# Security Policy

## Important Security Notes

⚠️ **This is a demonstration project for educational purposes.**

### Known Limitations

1. **Secrets Management**: 
   - `secrets.json` contains plaintext passwords
   - In production, use environment variables or a secret management service (e.g., AWS Secrets Manager, HashiCorp Vault)

2. **Key Storage**:
   - RSA keys are stored as files
   - In production, use a Key Management Service (KMS)

3. **Refresh Token Storage**:
   - Refresh tokens are stored in-memory
   - In production, use a persistent database with proper security

4. **HTTPS**:
   - This demo runs on HTTP
   - In production, **always use HTTPS/TLS**

5. **Password Hashing**:
   - Passwords are stored in plaintext
   - In production, use bcrypt, argon2, or similar


## Best Practices for Production

- Use environment variables for all secrets
- Enable HTTPS/TLS
- Hash passwords with bcrypt/argon2
- Store refresh tokens in Redis or a database
- Implement rate limiting
- Add request logging and monitoring
- Use short-lived access tokens (5-15 minutes)
- Implement token revocation
- Add CORS protection
- Use a reverse proxy (nginx, traefik)
