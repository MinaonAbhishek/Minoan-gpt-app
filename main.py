# from fastmcp import FastMCP
# import os
# import aiosqlite
# import tempfile
# import json
# from datetime import datetime

# # Use temporary directory which should be writable
# TEMP_DIR = tempfile.gettempdir()
# DB_PATH = os.path.join(TEMP_DIR, "minoan.db")

# print(f"Database path: {DB_PATH}")

# mcp = FastMCP("Minoan")

# def init_db():
#     """Initialize the Minoan product database with furniture and décor product names"""
#     try:
#         import sqlite3
#         with sqlite3.connect(DB_PATH) as c:
#             c.execute("PRAGMA journal_mode=WAL")
            
#             # Create simple products table with just names
#             c.execute("""
#                 CREATE TABLE IF NOT EXISTS products(
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     name TEXT NOT NULL
#                 )
#             """)
            
#             # Check if we need to seed data
#             cursor = c.execute("SELECT COUNT(*) FROM products")
#             count = cursor.fetchone()[0]
            
#             if count == 0:
#                 # Seed sample furniture and décor product names
#                 sample_products = [
#                     ("Modern Velvet Sofa",),
#                     ("Scandinavian Dining Table",),
#                     ("Industrial Floor Lamp",),
#                     ("Bohemian Area Rug",),
#                     ("Mid-Century Armchair",),
#                     ("Marble Coffee Table",),
#                     ("Ceramic Vase Set",),
#                     ("Platform Bed Frame",),
#                     ("Rattan Pendant Light",),
#                     ("Abstract Wall Art",)
#                 ]
                
#                 c.executemany("""
#                     INSERT INTO products(name) VALUES (?)
#                 """, sample_products)
                
#                 c.commit()
#                 print(f"Database initialized with {len(sample_products)} sample products")
#             else:
#                 print(f"Database already contains {count} products")
                
#     except Exception as e:
#         print(f"Database initialization error: {e}")
#         raise

# # Initialize database synchronously at module load
# init_db()

# @mcp.tool()
# async def get_products():
#     """Fetch all furniture and décor products from the Minoan catalog."""
#     try:
#         async with aiosqlite.connect(DB_PATH) as c:
#             cur = await c.execute("SELECT id, name FROM products ORDER BY name")
#             products = []
#             async for row in cur:
#                 products.append({
#                     "id": row[0],
#                     "name": row[1]
#                 })
            
#             return {
#                 "status": "success",
#                 "count": len(products),
#                 "products": products
#             }
#     except Exception as e:
#         return {"status": "error", "message": f"Error fetching products: {str(e)}"}

# @mcp.resource("minoan:///catalog", mime_type="application/json")
# def product_catalog():
#     """Provide the full product catalog as a resource."""
#     try:
#         import sqlite3
#         with sqlite3.connect(DB_PATH) as c:
#             cur = c.execute("SELECT id, name FROM products ORDER BY name")
#             products = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
            
#             catalog = {
#                 "store": "Minoan",
#                 "description": "Discover and purchase furniture and décor through natural conversation",
#                 "total_products": len(products),
#                 "products": products
#             }
            
#             return json.dumps(catalog, indent=2)
#     except Exception as e:
#         return json.dumps({"error": f"Could not load catalog: {str(e)}"}, indent=2)

# # Start the server
# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)

# from fastmcp import FastMCP
# import json
# import os
# import tempfile
# from difflib import get_close_matches

# # Initialize MCP app
# mcp = FastMCP("MinoanBrandDiscovery")

# # Paths
# TEMP_DIR = tempfile.gettempdir()
# DB_PATH = os.path.join(TEMP_DIR, "minoan_brand.db")
# BRAND_JSON = os.path.join(os.path.dirname(__file__), "brands.json")

# # Load brand data once
# try:
#     with open(BRAND_JSON, "r", encoding="utf-8") as f:
#         BRANDS = json.load(f)
#     print(f"✅ Loaded {len(BRANDS)} brands from brands.json")
# except Exception as e:
#     print(f"❌ Error loading brands.json: {e}")
#     BRANDS = []

# # ------------------------------------------------------------------------------
# # TOOL 1: Brand Recommendation
# # ------------------------------------------------------------------------------

# @mcp.tool()
# def recommend_brand(query: str) -> dict:
#     """
#     Recommend the best matching brand based on a user's product query.
#     Priority: keyword match > fuzzy match > fallback message.
#     """

#     query_lower = query.lower()
#     matches = []

#     for brand in BRANDS:
#         keywords = [kw.lower() for kw in brand.get("keywords", [])]

#         # 1️⃣ Direct keyword or substring match
#         if any(kw in query_lower for kw in keywords):
#             matches.append((brand, "keyword"))
#             continue

#         # 2️⃣ Fuzzy match (useful for near words, e.g. "bath towel" vs "towels")
#         for kw in keywords:
#             if get_close_matches(query_lower, [kw], cutoff=0.7):
#                 matches.append((brand, "fuzzy"))
#                 break

#     if matches:
#         # Prioritize keyword match first
#         matches.sort(key=lambda x: 0 if x[1] == "keyword" else 1)
#         top_brand = matches[0][0]
#         return {
#             "status": "success",
#             "brand": top_brand["brand_name"],
#             "url": top_brand["web_link"],
#             "match_type": matches[0][1],
#             "description": top_brand["description"],
#         }

#     return {
#         "status": "no_match",
#         "message": "No matching brand found for your query."
#     }

# # ------------------------------------------------------------------------------
# # TOOL 2: Get All Brands
# # ------------------------------------------------------------------------------

# @mcp.tool()
# def get_all_brands() -> dict:
#     """Return all available brands in the dataset."""
#     try:
#         return {
#             "status": "success",
#             "total": len(BRANDS),
#             "brands": [
#                 {"id": b["id"], "name": b["brand_name"], "url": b["web_link"]}
#                 for b in BRANDS
#             ],
#         }
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# # ------------------------------------------------------------------------------
# # RESOURCE: Brand Catalog
# # ------------------------------------------------------------------------------

# @mcp.resource("minoan:///brands", mime_type="application/json")
# def brand_catalog():
#     """Expose all brands as a JSON resource."""
#     try:
#         return json.dumps(
#             {
#                 "store": "Minoan Brand Discovery",
#                 "description": "AI brand recommender that suggests the best brand for a product type or query.",
#                 "total_brands": len(BRANDS),
#                 "brands": BRANDS,
#             },
#             indent=2,
#         )
#     except Exception as e:
#         return json.dumps({"error": str(e)}, indent=2)

# # ------------------------------------------------------------------------------
# # Run MCP server
# # ------------------------------------------------------------------------------

# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)

from fastmcp import FastMCP
import json
import os
import re
import secrets
import hashlib
import base64
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.requests import Request
import httpx
import jwt

mcp = FastMCP("MinoanBrandDiscovery")

# ---------------------------------------------------------------------------
# OAuth Configuration
# ---------------------------------------------------------------------------
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", "https://dev-my.minoan.com")
# Default to HTTPS for production - ChatGPT requires HTTPS
OAUTH_BASE_URL = os.getenv("OAUTH_BASE_URL", "https://minoan-app.fastmcp.app")
# User login page - where users authenticate
USER_LOGIN_PAGE = os.getenv("USER_LOGIN_PAGE", "https://dev-my.minoan.com/auth/login")
# Backend login API - where we authenticate users
LOGIN_API_URL = "https://devb2b-api.minoanexperience.com/public/account/login"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALG = "HS256"

# Note: JWT_SECRET_KEY is optional for basic OAuth flow (tokens are passed through)
# It's only needed if you want to verify JWT tokens yourself
# For production, you may want to verify tokens before storing them
if not JWT_SECRET_KEY:
    print("⚠️  WARNING: JWT_SECRET_KEY not set - token verification disabled")
    print("   Tokens will be passed through without verification")
    print("   Set JWT_SECRET_KEY if you need to verify tokens")

def get_base_url(request: Request = None) -> str:
    """
    Get the base URL for OAuth endpoints.
    Uses request headers if available, otherwise falls back to OAUTH_BASE_URL.
    Always uses HTTPS for production.
    """
    if request:
        # Try to get from request headers (for FastMCP Cloud)
        host = request.headers.get("host") or request.url.hostname
        if host:
            # Always use HTTPS in production
            return f"https://{host}"
    
    # Fall back to environment variable or default
    base_url = OAUTH_BASE_URL
    # Always ensure HTTPS (no localhost exceptions in production)
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://")
    return base_url


def validate_redirect_uri(redirect_uri: str) -> bool:
    """
    Validate that redirect URI is safe - requires HTTPS.
    ChatGPT requires HTTPS for all redirect URIs in production.
    """
    if not redirect_uri:
        return False
    # Require HTTPS for all URLs (no localhost exceptions in production)
    return redirect_uri.startswith("https://")

# In-memory store for authorization codes (expires after 10 minutes)
# In production, use Redis or a database
auth_codes: dict[str, dict] = {}

# In-memory store for registered OAuth clients (RFC 7591)
# In production, use a database
registered_clients: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# OAuth Helper Functions
# ---------------------------------------------------------------------------

def base64url_encode(data: bytes) -> str:
    """Base64URL encode without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def base64url_decode(data: str) -> bytes:
    """Base64URL decode."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def generate_code_verifier() -> str:
    """Generate PKCE code verifier."""
    return base64url_encode(secrets.token_bytes(32))


def generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge (S256)."""
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64url_encode(digest)


def verify_code_challenge(verifier: str, challenge: str) -> bool:
    """Verify PKCE code challenge."""
    expected = generate_code_challenge(verifier)
    return secrets.compare_digest(expected, challenge)


def create_authorization_code(state: str, code_challenge: str, redirect_uri: str) -> str:
    """Create and store an authorization code."""
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {
        "state": state,
        "code_challenge": code_challenge,
        "redirect_uri": redirect_uri,
        "expires_at": time.time() + 600,  # 10 minutes
    }
    print(f"🔐 Created authorization code: {code[:16]}... (expires in 10min)")
    return code


def get_authorization_code(code: str) -> dict | None:
    """Retrieve and validate authorization code."""
    if code not in auth_codes:
        return None
    data = auth_codes[code]
    if time.time() > data["expires_at"]:
        del auth_codes[code]
        return None
    return data


def cleanup_expired_codes():
    """Clean up expired authorization codes to prevent memory leaks."""
    current_time = time.time()
    expired = [code for code, data in list(auth_codes.items()) 
               if current_time > data.get("expires_at", 0)]
    for code in expired:
        del auth_codes[code]
    if expired:
        print(f"🧹 Cleaned up {len(expired)} expired authorization codes")
    return len(expired)


def consume_authorization_code(code: str) -> dict | None:
    """Retrieve and delete authorization code (one-time use)."""
    data = get_authorization_code(code)
    if data:
        del auth_codes[code]
        print(f"✅ Consumed authorization code: {code[:16]}...")
    return data


# ---------------------------------------------------------------------------
# Load brand data
# ---------------------------------------------------------------------------
BRAND_JSON = os.path.join(os.path.dirname(__file__), "brands.json")
with open(BRAND_JSON, "r", encoding="utf-8") as f:
    BRANDS = json.load(f)
print(f"✅ Loaded {len(BRANDS)} brands")

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def split_query(query: str):
    """Split complex query into meaningful product phrases."""
    # Keep multi-word terms (e.g. "smart locks", "bath towels")
    parts = re.split(r",| and | & | with ", query.lower())
    parts = [p.strip() for p in parts if len(p.strip()) > 2]
    return parts

def token_similarity(a, b):
    """Normalized token similarity (0-1)."""
    a, b = a.lower(), b.lower()
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.85
    return SequenceMatcher(None, a, b).ratio()

# ---------------------------------------------------------------------------
# TOOL: Robust Multi-Brand Recommender
# ---------------------------------------------------------------------------

@mcp.tool()
def recommend_brands(query: str, max_results: int = 10) -> dict:
    """
    Recommend multiple relevant brands using keyword + fuzzy logic.
    - Phrase-based parsing
    - Weighted scoring
    - Clean ranked output
    """

    query = query.strip().lower()
    if not query:
        return {"status": "error", "message": "Empty query."}

    phrases = split_query(query)
    results = []

    for brand in BRANDS:
        keywords = [kw.lower() for kw in brand.get("keywords", [])]
        score = 0.0
        matched = []

        for phrase in phrases:
            for kw in keywords:
                sim = token_similarity(phrase, kw)

                # Strong exact or inclusion match
                if sim >= 0.95:
                    score += 3.0
                    matched.append(kw)
                # Close fuzzy (only for longer words to avoid "rt" noise)
                elif sim >= 0.8 and len(phrase) >= 4 and len(kw) >= 4:
                    score += 1.5
                    matched.append(kw)

        if score > 0:
            results.append({
                "brand": brand["brand_name"],
                "url": brand["web_link"],
                "score": round(score, 2),
                "matched_keywords": list(set(matched)),
                "description": brand["description"]
            })

    if not results:
        return {"status": "no_match", "message": "No matching brands found."}

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "status": "success",
        "query": query,
        "total_matches": len(results),
        "brands": results[:max_results]
    }

# ---------------------------------------------------------------------------
# OAuth 2.1 + PKCE Endpoints for ChatGPT Integration
# ---------------------------------------------------------------------------

@mcp.custom_route(path="/.well-known/oauth-authorization-server", methods=["GET"])
async def oauth_authorization_server(request: Request) -> JSONResponse:
    """OAuth 2.1 discovery endpoint for ChatGPT."""
    base_url = get_base_url(request)
    response = JSONResponse(content={
        "issuer": OAUTH_ISSUER,
        "authorization_endpoint": USER_LOGIN_PAGE,  # User's existing login page
        "token_endpoint": f"{base_url}/auth/token",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "registration_endpoint": f"{base_url}/register",  # RFC 7591
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["brands:read"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["none"],  # PKCE only
        "response_modes_supported": ["query"],
    })
    # Add CORS headers for discovery endpoint
    # In production, restrict to specific origins via CORS_ALLOWED_ORIGINS env var
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
    origin = request.headers.get("origin")
    if "*" in allowed_origins or (origin and origin in allowed_origins):
        response.headers["Access-Control-Allow-Origin"] = origin if origin and origin in allowed_origins else "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@mcp.custom_route(path="/.well-known/jwks.json", methods=["GET"])
async def jwks(request: Request) -> JSONResponse:
    """
    JWKS endpoint for public key verification.
    Note: Since we use HS256 (symmetric), there's no public key.
    ChatGPT will need JWT_SECRET_KEY for verification, or we'd need to switch to RS256.
    For now, return an empty keys array with a note.
    """
    # For HS256, we can't provide a public key. ChatGPT would need the secret.
    # If switching to RS256, generate an RSA key pair and return the public key here.
    return JSONResponse(content={
        "keys": []
        # In production with RS256:
        # "keys": [{
        #     "kty": "RSA",
        #     "kid": "1",
        #     "use": "sig",
        #     "n": "...",  # RSA modulus (base64url)
        #     "e": "AQAB"  # RSA exponent
        # }]
    })


@mcp.custom_route(path="/auth/login", methods=["GET"])
async def auth_login(request: Request) -> HTMLResponse:
    """OAuth authorization endpoint - shows login form."""
    # Extract query parameters
    query_params = request.query_params
    response_type = query_params.get("response_type", "")
    client_id = query_params.get("client_id", "")
    redirect_uri = query_params.get("redirect_uri", "")
    state = query_params.get("state", "")
    code_challenge = query_params.get("code_challenge", "")
    code_challenge_method = query_params.get("code_challenge_method", "S256")
    scope = query_params.get("scope", "brands:read")
    
    if response_type != "code":
        raise HTTPException(status_code=400, detail="response_type must be 'code'")
    if code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="Only S256 code challenge method supported")
    if not validate_redirect_uri(redirect_uri):
        raise HTTPException(
            status_code=400, 
            detail="redirect_uri must use HTTPS"
        )

    # Store OAuth params in session (simplified - in production use proper sessions)
    # For now, pass via query params to the form

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Minoan Login</title>
        <style>
            body {{ font-family: -apple-system, Segoe UI, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
            h1 {{ font-size: 24px; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-size: 14px; color: #555; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #111827; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }}
            button:hover {{ background: #1f2937; }}
            .error {{ color: #dc2626; font-size: 14px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>Sign in to Minoan</h1>
        <form id="loginForm" method="POST" action="/auth/login">
            <input type="hidden" name="response_type" value="{response_type}">
            <input type="hidden" name="client_id" value="{client_id}">
            <input type="hidden" name="redirect_uri" value="{redirect_uri}">
            <input type="hidden" name="state" value="{state}">
            <input type="hidden" name="code_challenge" value="{code_challenge}">
            <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
            <input type="hidden" name="scope" value="{scope}">
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">Sign In</button>
            <div id="error" class="error" style="display: none;"></div>
        </form>
        
        <script>
            // Form submits normally to allow browser to follow redirect
            // No need for AJAX - the server returns a 302 redirect
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@mcp.custom_route(path="/auth/login", methods=["POST"])
async def auth_login_post(request: Request) -> RedirectResponse:
    """Handle login form submission and create authorization code."""
    # Parse form data
    try:
        form_data = await request.form()
    except Exception as e:
        print(f"❌ Error parsing form data: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    response_type = form_data.get("response_type", "")
    client_id = form_data.get("client_id", "")
    redirect_uri = form_data.get("redirect_uri", "")
    state = form_data.get("state", "")
    code_challenge = form_data.get("code_challenge", "")
    code_challenge_method = form_data.get("code_challenge_method", "")
    scope = form_data.get("scope", "")
    email = form_data.get("email", "")
    password = form_data.get("password", "")
    
    print(f"🔐 OAuth login attempt for: {email}")
    print(f"📋 Received parameters:")
    print(f"   - response_type: {response_type}")
    print(f"   - client_id: {client_id}")
    print(f"   - redirect_uri: {redirect_uri}")
    print(f"   - state: {state}")
    print(f"   - code_challenge: {code_challenge[:30] if code_challenge else 'MISSING'}...")
    
    # Validate required parameters - redirect with error if missing
    if not redirect_uri:
        print(f"❌ Missing redirect_uri")
        # Can't redirect without redirect_uri, so return error page
        return HTMLResponse(
            content="<h1>Error</h1><p>Missing redirect_uri parameter</p>",
            status_code=400
        )
    if not state:
        print(f"❌ Missing state - redirecting with error")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Missing+state+parameter"
        return RedirectResponse(url=error_redirect, status_code=302)
    if not code_challenge:
        print(f"❌ Missing code_challenge - redirecting with error")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Missing+code_challenge+parameter&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)

    # Call the actual login API
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            login_resp = await client.post(
                LOGIN_API_URL,
                json={"email": email, "password": password},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            login_resp.raise_for_status()
            login_data = login_resp.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ Login failed: {e.response.status_code}")
            # Return error page or redirect with error
            error_redirect = f"{redirect_uri}?error=access_denied&error_description=Invalid+email+or+password&state={state}"
            return RedirectResponse(url=error_redirect, status_code=302)
        except Exception as e:
            print(f"❌ Login error: {e}")
            error_redirect = f"{redirect_uri}?error=server_error&error_description={str(e).replace(' ', '+')}&state={state}"
            return RedirectResponse(url=error_redirect, status_code=302)

    # Extract token from response
    token_data = login_data.get("data", {})
    token = token_data.get("token")
    if not token:
        error_redirect = f"{redirect_uri}?error=server_error&error_description=Token+not+found&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)

    print(f"✅ Login successful, token extracted: {token[:20]}...")
    print(f"📋 Redirect URI: {redirect_uri}")
    print(f"📋 State: {state}")
    print(f"📋 Code Challenge: {code_challenge[:20]}...")

    # Validate redirect_uri
    if not validate_redirect_uri(redirect_uri):
        print(f"❌ Invalid redirect_uri: {redirect_uri}")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Invalid+redirect_uri&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)

    # Create authorization code
    try:
        auth_code = create_authorization_code(state, code_challenge, redirect_uri)
        
        # Store token with the code (for token exchange)
        auth_codes[auth_code]["token"] = token
        auth_codes[auth_code]["user_data"] = token_data
        
        # Build redirect URL - check if redirect_uri already has query params
        separator = "&" if "?" in redirect_uri else "?"
        redirect_url = f"{redirect_uri}{separator}code={auth_code}&state={state}"
        
        print(f"✅ Created authorization code: {auth_code[:16]}...")
        print(f"🔄 Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        print(f"❌ Error creating authorization code: {e}")
        import traceback
        traceback.print_exc()
        error_redirect = f"{redirect_uri}?error=server_error&error_description=Failed+to+create+authorization+code&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)


@mcp.custom_route(path="/auth/callback", methods=["GET"])
async def auth_callback(request: Request) -> RedirectResponse:
    """
    OAuth callback endpoint - called by user's login page after successful authentication.
    The login page at https://dev-my.minoan.com/auth/login should redirect here with:
    - token: JWT token from successful login
    - redirect_uri: Original OAuth redirect_uri
    - state: OAuth state parameter
    - code_challenge: PKCE code challenge
    - code_challenge_method: PKCE method (S256)
    """
    query_params = request.query_params
    token = query_params.get("token", "")
    redirect_uri = query_params.get("redirect_uri", "")
    state = query_params.get("state", "")
    code_challenge = query_params.get("code_challenge", "")
    code_challenge_method = query_params.get("code_challenge_method", "S256")
    
    print(f"🔄 OAuth callback received")
    print(f"📋 Token: {token[:20] if token else 'MISSING'}...")
    print(f"📋 Redirect URI: {redirect_uri}")
    print(f"📋 State: {state}")
    print(f"📋 Code Challenge: {code_challenge[:30] if code_challenge else 'MISSING'}...")
    
    # Validate required parameters
    if not token:
        print(f"❌ Missing token in callback")
        if redirect_uri:
            error_redirect = f"{redirect_uri}?error=server_error&error_description=Missing+token&state={state}"
            return RedirectResponse(url=error_redirect, status_code=302)
        return HTMLResponse(content="<h1>Error</h1><p>Missing token parameter</p>", status_code=400)
    
    if not redirect_uri:
        print(f"❌ Missing redirect_uri in callback")
        return HTMLResponse(content="<h1>Error</h1><p>Missing redirect_uri parameter</p>", status_code=400)
    
    if not state:
        print(f"❌ Missing state in callback")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Missing+state"
        return RedirectResponse(url=error_redirect, status_code=302)
    
    if not code_challenge:
        print(f"❌ Missing code_challenge in callback")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Missing+code_challenge&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)
    
    # Validate redirect_uri
    if not validate_redirect_uri(redirect_uri):
        print(f"❌ Invalid redirect_uri: {redirect_uri}")
        error_redirect = f"{redirect_uri}?error=invalid_request&error_description=Invalid+redirect_uri&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)
    
    # Create authorization code
    try:
        auth_code = create_authorization_code(state, code_challenge, redirect_uri)
        
        # Store token with the code (for token exchange)
        auth_codes[auth_code]["token"] = token
        # Store minimal user data (you can extract from token if needed)
        auth_codes[auth_code]["user_data"] = {}
        
        # Build redirect URL - check if redirect_uri already has query params
        separator = "&" if "?" in redirect_uri else "?"
        redirect_url = f"{redirect_uri}{separator}code={auth_code}&state={state}"
        
        print(f"✅ Created authorization code: {auth_code[:16]}...")
        print(f"🔄 Redirecting to ChatGPT: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
    except Exception as e:
        print(f"❌ Error creating authorization code: {e}")
        import traceback
        traceback.print_exc()
        error_redirect = f"{redirect_uri}?error=server_error&error_description=Failed+to+create+authorization+code&state={state}"
        return RedirectResponse(url=error_redirect, status_code=302)


@mcp.custom_route(path="/register", methods=["POST", "OPTIONS"])
async def register_client(request: Request) -> JSONResponse:
    """
    RFC 7591 Dynamic Client Registration endpoint.
    Allows ChatGPT to register itself as an OAuth client.
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        body = await request.json()
    except Exception as e:
        print(f"❌ Error parsing registration request: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "Invalid JSON body"}
        )
    
    base_url = get_base_url(request)
    
    print(f"📝 Client registration request")
    print(f"📋 Client name: {body.get('client_name', 'Unknown')}")
    print(f"📋 Redirect URIs: {body.get('redirect_uris', [])}")
    
    # Generate client_id and client_secret (though with PKCE, secret may not be needed)
    client_id = secrets.token_urlsafe(32)
    client_secret = secrets.token_urlsafe(32)
    
    # Store client registration
    registered_clients[client_id] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_name": body.get("client_name", "ChatGPT MCP Client"),
        "redirect_uris": body.get("redirect_uris", []),
        "grant_types": body.get("grant_types", ["authorization_code"]),
        "response_types": body.get("response_types", ["code"]),
        "scope": body.get("scope", "brands:read"),
        "token_endpoint_auth_method": body.get("token_endpoint_auth_method", "none"),  # PKCE
        "created_at": time.time(),
    }
    
    print(f"✅ Registered new OAuth client: {client_id[:16]}...")
    
    # Return client registration response (RFC 7591)
    response = JSONResponse(content={
        "client_id": client_id,
        "client_secret": client_secret,  # Optional with PKCE, but included for compatibility
        "client_id_issued_at": int(time.time()),
        "client_secret_expires_at": 0,  # 0 means never expires
        "registration_access_token": secrets.token_urlsafe(32),  # For client management
        "registration_client_uri": f"{base_url}/register/{client_id}",
        "redirect_uris": registered_clients[client_id]["redirect_uris"],
        "grant_types": registered_clients[client_id]["grant_types"],
        "response_types": registered_clients[client_id]["response_types"],
        "scope": registered_clients[client_id]["scope"],
        "token_endpoint_auth_method": registered_clients[client_id]["token_endpoint_auth_method"],
    })
    # Add CORS headers
    # In production, restrict to specific origins via CORS_ALLOWED_ORIGINS env var
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
    origin = request.headers.get("origin")
    if "*" in allowed_origins or (origin and origin in allowed_origins):
        response.headers["Access-Control-Allow-Origin"] = origin if origin and origin in allowed_origins else "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@mcp.custom_route(path="/auth/token", methods=["POST"])
async def auth_token(request: Request) -> JSONResponse:
    """OAuth token endpoint - exchanges authorization code for access token."""
    # Support both form data and JSON (OAuth 2.1 spec allows both)
    content_type = request.headers.get("content-type", "")
    
    try:
        if "application/json" in content_type:
            body = await request.json()
            grant_type = body.get("grant_type", "")
            code = body.get("code", "")
            redirect_uri = body.get("redirect_uri", "")
            code_verifier = body.get("code_verifier", "")
        else:
            form_data = await request.form()
            grant_type = form_data.get("grant_type", "")
            code = form_data.get("code", "")
            redirect_uri = form_data.get("redirect_uri", "")
            code_verifier = form_data.get("code_verifier", "")
    except Exception as e:
        print(f"❌ Error parsing request: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "Invalid request format"}
        )
    
    print(f"🔐 Token exchange request")
    print(f"📋 Grant type: {grant_type}")
    print(f"📋 Code: {code[:16] if code else 'MISSING'}...")
    print(f"📋 Redirect URI: {redirect_uri}")
    print(f"📋 Code verifier: {code_verifier[:20] if code_verifier else 'MISSING'}...")
    
    # Validate grant_type
    if grant_type != "authorization_code":
        return JSONResponse(
            status_code=400,
            content={"error": "unsupported_grant_type", "error_description": "grant_type must be 'authorization_code'"}
        )
    
    # Validate required parameters
    if not code:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "Missing code parameter"}
        )
    if not redirect_uri:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "Missing redirect_uri parameter"}
        )
    if not code_verifier:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "Missing code_verifier parameter"}
        )

    # Retrieve and validate authorization code
    code_data = consume_authorization_code(code)
    if not code_data:
        print(f"❌ Invalid or expired authorization code")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant", "error_description": "Invalid or expired authorization code"}
        )

    # Verify PKCE
    if not verify_code_challenge(code_verifier, code_data["code_challenge"]):
        print(f"❌ PKCE verification failed")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant", "error_description": "Invalid code_verifier"}
        )

    # Verify redirect_uri matches
    if code_data["redirect_uri"] != redirect_uri:
        print(f"❌ Redirect URI mismatch: expected {code_data['redirect_uri']}, got {redirect_uri}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_grant", "error_description": "redirect_uri mismatch"}
        )

    # Get stored token
    token = code_data.get("token")
    if not token:
        print(f"❌ Token not found in authorization code")
        return JSONResponse(
            status_code=500,
            content={"error": "server_error", "error_description": "Token not found in authorization code"}
        )

    print(f"✅ Token exchange successful")
    print(f"📋 Access token: {token[:20]}...")

    # Return OAuth token response (OAuth 2.1 format)
    return JSONResponse(content={
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,  # 1 hour (adjust based on your token expiry)
        "scope": "brands:read",
    })


# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------

@mcp.custom_route(path="/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    # Clean up expired codes on health check (simple cleanup mechanism)
    cleanup_expired_codes()
    
    return JSONResponse(content={
        "status": "healthy",
        "service": "Minoan OAuth MCP Server",
        "timestamp": time.time(),
        "brands_loaded": len(BRANDS),
        "active_auth_codes": len(auth_codes),
        "registered_clients": len(registered_clients),
        "jwt_secret_configured": bool(JWT_SECRET_KEY),
    })


# ---------------------------------------------------------------------------
# Run MCP server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Starting Minoan OAuth server on http://0.0.0.0:8000")
    print(f"📋 OAuth Discovery: {OAUTH_BASE_URL}/.well-known/oauth-authorization-server")
    print(f"🔑 JWKS: {OAUTH_BASE_URL}/.well-known/jwks.json")
    print(f"📝 Client Registration: {OAUTH_BASE_URL}/register (RFC 7591)")
    print(f"🔐 Authorization Endpoint (User Login): {USER_LOGIN_PAGE}")
    print(f"🔄 OAuth Callback: {OAUTH_BASE_URL}/auth/callback")
    print(f"🎫 Token Endpoint: {OAUTH_BASE_URL}/auth/token")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
