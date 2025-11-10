# Quick Integration Guide - Fix Login Redirect Issue

## Problem

After successful login on `https://dev-my.minoan.com/auth/login`, the page doesn't redirect to complete the OAuth flow.

## Solution

Your login page needs to redirect to our callback endpoint after successful login.

## Quick Fix (3 Steps)

### Step 1: Extract OAuth Parameters

When ChatGPT redirects to your login page, it includes these query parameters:
- `redirect_uri` - Where to send user after OAuth
- `state` - CSRF protection token
- `code_challenge` - PKCE challenge
- `code_challenge_method` - Should be "S256"

**Extract them from the URL:**
```javascript
const urlParams = new URLSearchParams(window.location.search);
const oauthParams = {
  redirect_uri: urlParams.get('redirect_uri'),
  state: urlParams.get('state'),
  code_challenge: urlParams.get('code_challenge'),
  code_challenge_method: urlParams.get('code_challenge_method'),
};
```

### Step 2: After Successful Login

After your login API call succeeds, get the token and redirect:

```javascript
// After login API call
const data = await response.json();
const token = data.data?.token; // Extract token from response

if (token && oauthParams.redirect_uri) {
  // Build callback URL
  const callbackUrl = new URL('https://minoan-app.fastmcp.app/auth/callback');
  callbackUrl.searchParams.set('token', token);
  callbackUrl.searchParams.set('redirect_uri', oauthParams.redirect_uri);
  callbackUrl.searchParams.set('state', oauthParams.state);
  callbackUrl.searchParams.set('code_challenge', oauthParams.code_challenge);
  callbackUrl.searchParams.set('code_challenge_method', 'S256');
  
  // Redirect to callback
  window.location.href = callbackUrl.toString();
}
```

### Step 3: Error Handling

If login fails, redirect with error:

```javascript
if (!response.ok) {
  const errorUrl = new URL(oauthParams.redirect_uri);
  errorUrl.searchParams.set('error', 'access_denied');
  errorUrl.searchParams.set('error_description', 'Login failed');
  errorUrl.searchParams.set('state', oauthParams.state);
  window.location.href = errorUrl.toString();
}
```

## Complete Example

See `LOGIN_PAGE_COMPLETE_EXAMPLE.html` for a full working example you can use as a reference.

## Testing

1. **Test URL** (replace with actual values):
   ```
   https://dev-my.minoan.com/auth/login?
     response_type=code&
     redirect_uri=https://chatgpt.com/connector_platform_oauth_redirect&
     state=test123&
     code_challenge=test_challenge&
     code_challenge_method=S256
   ```

2. **Expected Flow**:
   - User sees login form
   - User enters credentials
   - Login API called
   - Token received
   - Redirect to: `https://minoan-app.fastmcp.app/auth/callback?token=...&redirect_uri=...&state=...&code_challenge=...`
   - Our callback creates auth code
   - Redirect to: `https://chatgpt.com/connector_platform_oauth_redirect?code=AUTH_CODE&state=test123`

## Debugging

Check your browser console and network tab:
- Look for the redirect to `/auth/callback`
- Check if all parameters are being passed
- Verify token is in the response

Check server logs for:
- `🔄 OAuth callback received`
- `✅ Created authorization code`
- `🔄 Redirecting to ChatGPT`

## Common Issues

1. **Missing OAuth parameters**: Make sure to preserve them from the initial URL
2. **Token not extracted**: Check `data.data.token` vs `data.token` in your API response
3. **Redirect not happening**: Check browser console for JavaScript errors
4. **CORS issues**: Shouldn't be an issue since it's a redirect, not an AJAX call

## Need Help?

If you're using a specific framework (React, Vue, Angular, etc.), let me know and I can provide framework-specific code.

