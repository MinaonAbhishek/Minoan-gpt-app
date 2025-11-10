# Login Page Integration Guide

## Overview

Your login page at `https://dev-my.minoan.com/auth/login` needs to integrate with the OAuth callback endpoint to complete the OAuth flow.

## OAuth Flow

1. **ChatGPT redirects user to your login page**:
   ```
   GET https://dev-my.minoan.com/auth/login?
     response_type=code&
     client_id=...&
     redirect_uri=https://chatgpt.com/connector_platform_oauth_redirect&
     state=...&
     code_challenge=...&
     code_challenge_method=S256&
     scope=brands:read
   ```

2. **User logs in** on your page

3. **After successful login**, your page should:
   - Get the JWT token from the login API response
   - Redirect to our callback endpoint with the token and OAuth parameters

4. **Our callback endpoint** creates the authorization code and redirects to ChatGPT

## Integration Steps

### Step 1: Extract OAuth Parameters

When your login page receives the OAuth request, extract these parameters from the query string:
- `response_type` (should be "code")
- `client_id`
- `redirect_uri` (ChatGPT's callback URL)
- `state` (CSRF protection)
- `code_challenge` (PKCE challenge)
- `code_challenge_method` (should be "S256")
- `scope` (should be "brands:read")

### Step 2: Store OAuth Parameters

Store these parameters (in session, localStorage, or pass them through the login form) so they're available after login.

### Step 3: After Successful Login

After the user successfully logs in and you receive the token from your API:

```javascript
// Example JavaScript (adjust to your framework)
async function handleLoginSuccess(token, oauthParams) {
  // Build callback URL
  const callbackUrl = new URL('https://minoan-app.fastmcp.app/auth/callback');
  
  // Add token and OAuth parameters
  callbackUrl.searchParams.set('token', token);
  callbackUrl.searchParams.set('redirect_uri', oauthParams.redirect_uri);
  callbackUrl.searchParams.set('state', oauthParams.state);
  callbackUrl.searchParams.set('code_challenge', oauthParams.code_challenge);
  callbackUrl.searchParams.set('code_challenge_method', oauthParams.code_challenge_method);
  
  // Redirect to callback
  window.location.href = callbackUrl.toString();
}
```

### Step 4: Callback Endpoint

Our callback endpoint (`https://minoan-app.fastmcp.app/auth/callback`) will:
1. Validate the token and parameters
2. Create an authorization code
3. Redirect to ChatGPT: `redirect_uri?code=AUTH_CODE&state=STATE`

## Example Implementation

### React/Next.js Example

```javascript
// pages/auth/login.js or similar
import { useRouter } from 'next/router';
import { useState } from 'react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Extract OAuth params from query string
  const oauthParams = {
    response_type: router.query.response_type,
    client_id: router.query.client_id,
    redirect_uri: router.query.redirect_uri,
    state: router.query.state,
    code_challenge: router.query.code_challenge,
    code_challenge_method: router.query.code_challenge_method,
    scope: router.query.scope,
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Call your login API
      const response = await fetch('https://devb2b-api.minoanexperience.com/public/account/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await response.json();
      const token = data.data?.token;
      
      if (token) {
        // Redirect to OAuth callback
        const callbackUrl = new URL('https://minoan-app.fastmcp.app/auth/callback');
        callbackUrl.searchParams.set('token', token);
        callbackUrl.searchParams.set('redirect_uri', oauthParams.redirect_uri);
        callbackUrl.searchParams.set('state', oauthParams.state);
        callbackUrl.searchParams.set('code_challenge', oauthParams.code_challenge);
        callbackUrl.searchParams.set('code_challenge_method', oauthParams.code_challenge_method);
        
        window.location.href = callbackUrl.toString();
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

### Plain HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Minoan Login</title>
</head>
<body>
  <form id="loginForm">
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="password" placeholder="Password" required>
    <button type="submit">Sign In</button>
  </form>
  
  <script>
    // Extract OAuth params from URL
    const urlParams = new URLSearchParams(window.location.search);
    const oauthParams = {
      redirect_uri: urlParams.get('redirect_uri'),
      state: urlParams.get('state'),
      code_challenge: urlParams.get('code_challenge'),
      code_challenge_method: urlParams.get('code_challenge_method'),
    };
    
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      try {
        const response = await fetch('https://devb2b-api.minoanexperience.com/public/account/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        const token = data.data?.token;
        
        if (token) {
          // Redirect to OAuth callback
          const callbackUrl = new URL('https://minoan-app.fastmcp.app/auth/callback');
          callbackUrl.searchParams.set('token', token);
          callbackUrl.searchParams.set('redirect_uri', oauthParams.redirect_uri);
          callbackUrl.searchParams.set('state', oauthParams.state);
          callbackUrl.searchParams.set('code_challenge', oauthParams.code_challenge);
          callbackUrl.searchParams.set('code_challenge_method', oauthParams.code_challenge_method);
          
          window.location.href = callbackUrl.toString();
        }
      } catch (error) {
        console.error('Login failed:', error);
        alert('Login failed. Please try again.');
      }
    });
  </script>
</body>
</html>
```

## Important Notes

1. **Preserve OAuth Parameters**: Make sure to preserve all OAuth parameters through the login flow
2. **Token Extraction**: Extract the token from `data.data.token` in the login API response
3. **Error Handling**: If login fails, you can redirect to ChatGPT with an error:
   ```
   redirect_uri?error=access_denied&error_description=Login+failed&state=STATE
   ```
4. **HTTPS Required**: All redirects must use HTTPS
5. **State Parameter**: Always include the `state` parameter in redirects for CSRF protection

## Testing

1. Test the flow manually:
   - Visit: `https://dev-my.minoan.com/auth/login?response_type=code&redirect_uri=https://chatgpt.com/connector_platform_oauth_redirect&state=test123&code_challenge=test&code_challenge_method=S256`
   - Log in
   - Verify redirect to callback endpoint
   - Verify redirect to ChatGPT with authorization code

2. Check server logs for:
   - `🔄 OAuth callback received`
   - `✅ Created authorization code`
   - `🔄 Redirecting to ChatGPT`

## Callback Endpoint URL

**Production**: `https://minoan-app.fastmcp.app/auth/callback`

Make sure your login page redirects to this endpoint after successful authentication.

