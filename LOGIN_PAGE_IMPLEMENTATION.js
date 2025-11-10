/**
 * OAuth Integration for Minoan Login Page
 * 
 * Add this code to your login page at https://dev-my.minoan.com/auth/login
 * 
 * This handles:
 * 1. Extracting OAuth parameters from URL
 * 2. Calling your login API
 * 3. Redirecting to OAuth callback with token
 */

// Configuration
const OAUTH_CALLBACK_URL = 'https://minoan-app.fastmcp.app/auth/callback';
const LOGIN_API_URL = 'https://devb2b-api.minoanexperience.com/public/account/login';

/**
 * Extract OAuth parameters from URL query string
 */
function getOAuthParams() {
  const urlParams = new URLSearchParams(window.location.search);
  return {
    response_type: urlParams.get('response_type'),
    client_id: urlParams.get('client_id'),
    redirect_uri: urlParams.get('redirect_uri'),
    state: urlParams.get('state'),
    code_challenge: urlParams.get('code_challenge'),
    code_challenge_method: urlParams.get('code_challenge_method') || 'S256',
    scope: urlParams.get('scope') || 'brands:read',
  };
}

/**
 * Check if this is an OAuth request
 */
function isOAuthRequest() {
  const params = getOAuthParams();
  return params.response_type === 'code' && params.redirect_uri && params.state;
}

/**
 * Redirect to OAuth callback with token
 */
function redirectToOAuthCallback(token, oauthParams) {
  const callbackUrl = new URL(OAUTH_CALLBACK_URL);
  
  // Add token and OAuth parameters
  callbackUrl.searchParams.set('token', token);
  callbackUrl.searchParams.set('redirect_uri', oauthParams.redirect_uri);
  callbackUrl.searchParams.set('state', oauthParams.state);
  callbackUrl.searchParams.set('code_challenge', oauthParams.code_challenge);
  callbackUrl.searchParams.set('code_challenge_method', oauthParams.code_challenge_method);
  
  console.log('🔄 Redirecting to OAuth callback:', callbackUrl.toString());
  window.location.href = callbackUrl.toString();
}

/**
 * Redirect to ChatGPT with error
 */
function redirectWithError(oauthParams, error, description) {
  if (!oauthParams.redirect_uri) {
    console.error('Cannot redirect: missing redirect_uri');
    alert(`Error: ${description}`);
    return;
  }
  
  const errorUrl = new URL(oauthParams.redirect_uri);
  errorUrl.searchParams.set('error', error);
  errorUrl.searchParams.set('error_description', description);
  if (oauthParams.state) {
    errorUrl.searchParams.set('state', oauthParams.state);
  }
  
  console.error('❌ Redirecting with error:', error, description);
  window.location.href = errorUrl.toString();
}

/**
 * Handle login form submission
 */
async function handleLogin(email, password, oauthParams) {
  try {
    console.log('🔐 Attempting login for:', email);
    
    // Call login API
    const response = await fetch(LOGIN_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ Login failed:', response.status, errorData);
      redirectWithError(
        oauthParams,
        'access_denied',
        'Invalid email or password'
      );
      return;
    }
    
    const data = await response.json();
    console.log('✅ Login successful');
    
    // Extract token from response
    const token = data?.data?.token || data?.token;
    
    if (!token) {
      console.error('❌ Token not found in response:', data);
      redirectWithError(
        oauthParams,
        'server_error',
        'Token not found in login response'
      );
      return;
    }
    
    console.log('✅ Token extracted, redirecting to callback');
    
    // Redirect to OAuth callback
    redirectToOAuthCallback(token, oauthParams);
    
  } catch (error) {
    console.error('❌ Login error:', error);
    redirectWithError(
      oauthParams,
      'server_error',
      `Login error: ${error.message}`
    );
  }
}

// Export for use in your login page
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getOAuthParams,
    isOAuthRequest,
    handleLogin,
    redirectToOAuthCallback,
    redirectWithError,
  };
}

