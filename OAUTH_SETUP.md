# OAuth 2.1 + PKCE Implementation for ChatGPT Integration

## Overview

This implementation adds OAuth 2.1 + PKCE support to your Minoan FastMCP server, enabling ChatGPT to authenticate users and access protected resources.

## Endpoints

### 1. OAuth Discovery
- **GET** `/.well-known/oauth-authorization-server`
  - Returns OAuth 2.1 metadata for ChatGPT discovery
  - Includes authorization endpoint, token endpoint, JWKS URI, and supported methods

### 2. JWKS (JSON Web Key Set)
- **GET** `/.well-known/jwks.json`
  - Returns public keys for JWT verification
  - **Note**: Currently returns empty keys array because we use HS256 (symmetric)
  - For production with RS256, generate RSA key pair and return public key here

### 3. Authorization Endpoint
- **GET** `/auth/login`
  - Shows login form to users
  - Accepts OAuth parameters: `response_type`, `client_id`, `redirect_uri`, `state`, `code_challenge`, `code_challenge_method`, `scope`
  - Returns HTML login form

- **POST** `/auth/login`
  - Processes login credentials
  - Calls your backend API: `https://devb2b-api.minoanexperience.com/public/account/login`
  - Creates authorization code with PKCE challenge
  - Redirects to `redirect_uri` with `code` and `state`

### 4. Token Endpoint
- **POST** `/auth/token`
  - Exchanges authorization code for access token
  - Verifies PKCE code verifier
  - Returns OAuth token response with `access_token`, `token_type`, `expires_in`, `scope`

## OAuth Flow

1. **ChatGPT initiates OAuth**:
   ```
   GET /auth/login?response_type=code&client_id=chatgpt&redirect_uri=...&state=...&code_challenge=...&code_challenge_method=S256
   ```

2. **User logs in** via the HTML form

3. **Server creates authorization code** and redirects:
   ```
   GET redirect_uri?code=AUTH_CODE&state=STATE
   ```

4. **ChatGPT exchanges code for token**:
   ```
   POST /auth/token
   grant_type=authorization_code&code=AUTH_CODE&redirect_uri=...&code_verifier=VERIFIER
   ```

5. **Server returns access token**:
   ```json
   {
     "access_token": "eyJhbGci...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "scope": "brands:read"
   }
   ```

## Environment Variables

Set these before running:

```bash
export OAUTH_ISSUER="https://dev-my.minoan.com"  # Your OAuth issuer URL
export OAUTH_BASE_URL="http://localhost:8000"    # Your server base URL
export JWT_SECRET_KEY="your-secret-key"           # Secret for JWT verification
```

## Testing the OAuth Flow

### 1. Test Discovery Endpoint

```bash
curl http://localhost:8000/.well-known/oauth-authorization-server | jq .
```

Expected response:
```json
{
  "issuer": "https://dev-my.minoan.com",
  "authorization_endpoint": "http://localhost:8000/auth/login",
  "token_endpoint": "http://localhost:8000/auth/token",
  "jwks_uri": "http://localhost:8000/.well-known/jwks.json",
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["brands:read"],
  ...
}
```

### 2. Test Authorization Flow (Manual)

1. Generate PKCE values:
```python
import secrets
import hashlib
import base64

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

code_verifier = base64url_encode(secrets.token_bytes(32))
code_challenge = base64url_encode(hashlib.sha256(code_verifier.encode()).digest())
state = secrets.token_urlsafe(16)

print(f"Code Verifier: {code_verifier}")
print(f"Code Challenge: {code_challenge}")
print(f"State: {state}")
```

2. Open authorization URL in browser:
```
http://localhost:8000/auth/login?response_type=code&client_id=test&redirect_uri=http://localhost:8000/callback&state=STATE&code_challenge=CHALLENGE&code_challenge_method=S256
```

3. After login, you'll be redirected to:
```
http://localhost:8000/callback?code=AUTH_CODE&state=STATE
```

4. Exchange code for token:
```bash
curl -X POST http://localhost:8000/auth/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=http://localhost:8000/callback" \
  -d "code_verifier=CODE_VERIFIER"
```

### 3. Test with ChatGPT

When configuring your MCP server in ChatGPT:

1. **Provide OAuth Discovery URL**:
   ```
   https://dev-my.minoan.com/.well-known/oauth-authorization-server
   ```

2. **ChatGPT will**:
   - Fetch discovery metadata
   - Redirect user to `/auth/login` with PKCE parameters
   - User logs in
   - Receive authorization code
   - Exchange code for access token
   - Use token in `Authorization: Bearer <token>` header for API calls

## Important Notes

### JWKS and HS256

Your backend uses **HS256** (symmetric encryption), which means:
- There's no public key to share
- ChatGPT needs the `JWT_SECRET_KEY` to verify tokens
- The JWKS endpoint currently returns an empty keys array

**Options**:
1. **Share secret with ChatGPT** (if supported by their platform)
2. **Switch to RS256** (asymmetric) and generate RSA key pair:
   ```python
   from cryptography.hazmat.primitives.asymmetric import rsa
   from cryptography.hazmat.primitives import serialization
   
   private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
   public_key = private_key.public_key()
   
   # Return public key in JWKS format
   ```

### Authorization Code Storage

Currently using **in-memory dictionary** for authorization codes:
- Codes expire after 10 minutes
- Codes are single-use (deleted after exchange)
- **For production**: Use Redis or a database for distributed systems

### Security Considerations

1. **HTTPS in Production**: Always use HTTPS for OAuth endpoints
2. **State Parameter**: Validates CSRF protection
3. **PKCE**: Prevents authorization code interception
4. **Code Expiry**: Authorization codes expire after 10 minutes
5. **Redirect URI Validation**: Ensure `redirect_uri` matches exactly

## Logging

The server logs OAuth events:
- `🔐 OAuth login attempt for: <email>`
- `✅ Login successful, token extracted: <token>...`
- `🔐 Created authorization code: <code>...`
- `✅ Consumed authorization code: <code>...`
- `✅ Token exchange successful for user`

## Troubleshooting

### "Invalid or expired authorization code"
- Code expired (10 min timeout)
- Code already used (single-use)
- Code not found in storage

### "Invalid code_verifier"
- PKCE verification failed
- Code verifier doesn't match code challenge
- Ensure using S256 method

### "redirect_uri mismatch"
- Redirect URI in token request doesn't match authorization request
- Must be exact match (including protocol, domain, path, query params)

## Next Steps

1. **Deploy to production** with HTTPS
2. **Update OAUTH_BASE_URL** to your production domain
3. **Configure ChatGPT** with your OAuth discovery URL
4. **Monitor logs** for authentication attempts
5. **Consider switching to RS256** for better key management

