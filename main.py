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
from fastapi import Request, HTTPException, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.responses import Response
import httpx
import jwt

mcp = FastMCP("MinoanBrandDiscovery")
app = mcp.app  # Access underlying FastAPI app

# ---------------------------------------------------------------------------
# OAuth Configuration
# ---------------------------------------------------------------------------
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", "https://dev-my.minoan.com")
OAUTH_BASE_URL = os.getenv("OAUTH_BASE_URL", "http://localhost:8000")
LOGIN_API_URL = "https://devb2b-api.minoanexperience.com/public/account/login"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALG = "HS256"

# In-memory store for authorization codes (expires after 10 minutes)
# In production, use Redis or a database
auth_codes: dict[str, dict] = {}

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

@app.get("/.well-known/oauth-authorization-server", response_class=JSONResponse)
async def oauth_authorization_server():
    """OAuth 2.1 discovery endpoint for ChatGPT."""
    return {
        "issuer": OAUTH_ISSUER,
        "authorization_endpoint": f"{OAUTH_BASE_URL}/auth/login",
        "token_endpoint": f"{OAUTH_BASE_URL}/auth/token",
        "jwks_uri": f"{OAUTH_BASE_URL}/.well-known/jwks.json",
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["brands:read"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["none"],  # PKCE only
    }


@app.get("/.well-known/jwks.json", response_class=JSONResponse)
async def jwks():
    """
    JWKS endpoint for public key verification.
    Note: Since we use HS256 (symmetric), there's no public key.
    ChatGPT will need JWT_SECRET_KEY for verification, or we'd need to switch to RS256.
    For now, return an empty keys array with a note.
    """
    # For HS256, we can't provide a public key. ChatGPT would need the secret.
    # If switching to RS256, generate an RSA key pair and return the public key here.
    return {
        "keys": []
        # In production with RS256:
        # "keys": [{
        #     "kty": "RSA",
        #     "kid": "1",
        #     "use": "sig",
        #     "n": "...",  # RSA modulus (base64url)
        #     "e": "AQAB"  # RSA exponent
        # }]
    }


@app.get("/auth/login", response_class=HTMLResponse)
async def auth_login(
    response_type: str = Query(..., description="Must be 'code'"),
    client_id: str = Query(..., description="OAuth client ID"),
    redirect_uri: str = Query(..., description="Callback URI"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    code_challenge: str = Query(..., description="PKCE code challenge"),
    code_challenge_method: str = Query("S256", description="PKCE method (S256)"),
    scope: str = Query("brands:read", description="Requested scopes"),
):
    """OAuth authorization endpoint - shows login form."""
    if response_type != "code":
        raise HTTPException(status_code=400, detail="response_type must be 'code'")
    if code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="Only S256 code challenge method supported")

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


@app.post("/auth/login")
async def auth_login_post(
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
    code_challenge: str = Form(...),
    code_challenge_method: str = Form(...),
    scope: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """Handle login form submission and create authorization code."""
    print(f"🔐 OAuth login attempt for: {email}")

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

    # Create authorization code
    auth_code = create_authorization_code(state, code_challenge, redirect_uri)

    # Store token with the code (for token exchange)
    auth_codes[auth_code]["token"] = token
    auth_codes[auth_code]["user_data"] = token_data

    # Redirect to callback with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)


@app.post("/auth/token", response_class=JSONResponse)
async def auth_token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str = Form(..., description="PKCE code verifier"),
):
    """OAuth token endpoint - exchanges authorization code for access token."""
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="grant_type must be 'authorization_code'")

    print(f"🔐 Token exchange request for code: {code[:16]}...")

    # Retrieve and validate authorization code
    code_data = consume_authorization_code(code)
    if not code_data:
        raise HTTPException(status_code=400, detail="Invalid or expired authorization code")

    # Verify PKCE
    if not verify_code_challenge(code_verifier, code_data["code_challenge"]):
        print(f"❌ PKCE verification failed")
        raise HTTPException(status_code=400, detail="Invalid code_verifier")

    # Verify redirect_uri matches
    if code_data["redirect_uri"] != redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri mismatch")

    # Get stored token
    token = code_data.get("token")
    if not token:
        raise HTTPException(status_code=500, detail="Token not found in authorization code")

    print(f"✅ Token exchange successful for user")

    # Return OAuth token response
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,  # 1 hour (adjust based on your token expiry)
        "scope": "brands:read",
    }


# ---------------------------------------------------------------------------
# Run MCP server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Starting Minoan OAuth server on http://0.0.0.0:8000")
    print(f"📋 OAuth Discovery: {OAUTH_BASE_URL}/.well-known/oauth-authorization-server")
    print(f"🔑 JWKS: {OAUTH_BASE_URL}/.well-known/jwks.json")
    print(f"🔐 Authorization: {OAUTH_BASE_URL}/auth/login")
    print(f"🎫 Token: {OAUTH_BASE_URL}/auth/token")
    mcp.run(transport="http", host="0.0.0.0", port=8000)
