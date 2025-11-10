# OAuth Flow Explanation

## Current Configuration Issue

**Problem**: The OAuth discovery endpoint points to `https://dev-my.minoan.com/auth/login` as the authorization endpoint, but that page cannot create authorization codes because:
- Authorization code creation logic is in our FastMCP server
- The external login page doesn't have access to our server's code storage

## How OAuth Flow Should Work

### Option 1: Use Our Server's Authorization Endpoint (RECOMMENDED)

**Flow:**
1. **ChatGPT fetches discovery**: `GET https://minoan-app.fastmcp.app/.well-known/oauth-authorization-server`
   - Returns: `authorization_endpoint: https://minoan-app.fastmcp.app/auth/login`

2. **ChatGPT registers client**: `POST https://minoan-app.fastmcp.app/register`
   - Receives: `client_id`, `client_secret`

3. **ChatGPT redirects user**: `GET https://minoan-app.fastmcp.app/auth/login?response_type=code&client_id=...&redirect_uri=...&state=...&code_challenge=...`
   - User sees login form on our server
   - User enters credentials

4. **User submits login**: `POST https://minoan-app.fastmcp.app/auth/login`
   - Our server calls `https://devb2b-api.minoanexperience.com/public/account/login`
   - Our server creates authorization code
   - Our server redirects: `redirect_uri?code=AUTH_CODE&state=STATE`

5. **ChatGPT exchanges code**: `POST https://minoan-app.fastmcp.app/auth/token`
   - Sends: `grant_type=authorization_code&code=AUTH_CODE&code_verifier=...`
   - Receives: `access_token`

6. **ChatGPT uses token**: `Authorization: Bearer <access_token>`

### Option 2: Use External Login Page (Requires Integration)

**Flow:**
1. **ChatGPT redirects user**: `GET https://dev-my.minoan.com/auth/login?response_type=code&...`
   - User sees login form on your page
   - User enters credentials

2. **Your login page authenticates**: Calls `https://devb2b-api.minoanexperience.com/public/account/login`

3. **Your login page creates code**: Must call our server API to create authorization code
   - `POST https://minoan-app.fastmcp.app/auth/create-code`
   - With: `code_challenge`, `redirect_uri`, `state`, `token` (from login)
   - Receives: `authorization_code`

4. **Your login page redirects**: `redirect_uri?code=AUTH_CODE&state=STATE`

5. **ChatGPT exchanges code**: Same as Option 1

**Problem**: This requires creating a new API endpoint on our server for code creation, and your login page needs to integrate with it.

## Recommendation

**Use Option 1** - Point the authorization endpoint to our server's `/auth/login` endpoint. This is simpler and already fully implemented.

## Fix Required

Change the `AUTHORIZATION_ENDPOINT` to use our server's endpoint:

```python
AUTHORIZATION_ENDPOINT = f"{OAUTH_BASE_URL}/auth/login"
```

Or remove the `AUTHORIZATION_ENDPOINT` variable and use `get_base_url(request)` directly in the discovery endpoint.

