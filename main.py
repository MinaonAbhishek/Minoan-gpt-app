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
import tempfile
from difflib import get_close_matches
import re

mcp = FastMCP("MinoanBrandDiscovery")

# Paths
TEMP_DIR = tempfile.gettempdir()
BRAND_JSON = os.path.join(os.path.dirname(__file__), "brands.json")

# Load brand data
try:
    with open(BRAND_JSON, "r", encoding="utf-8") as f:
        BRANDS = json.load(f)
    print(f"✅ Loaded {len(BRANDS)} brands from brands.json")
except Exception as e:
    print(f"❌ Error loading brands.json: {e}")
    BRANDS = []

# ------------------------------------------------------------------------------
# TOOL: Multi-Brand Recommendation
# ------------------------------------------------------------------------------

@mcp.tool()
def recommend_brands(query: str) -> dict:
    """
    Recommend one or more brands for a complex product query.
    Splits query into parts and returns all matching brands.
    """

    query = query.lower()
    # Split query into possible product phrases
    parts = re.split(r"[,\sand]+", query)
    parts = [p.strip() for p in parts if len(p.strip()) > 1]

    found_brands = []

    for part in parts:
        for brand in BRANDS:
            keywords = [kw.lower() for kw in brand.get("keywords", [])]

            # 1️⃣ Direct match
            if any(kw in part for kw in keywords):
                found_brands.append({
                    "brand": brand["brand_name"],
                    "url": brand["web_link"],
                    "match_type": "keyword",
                    "matched_with": part,
                    "description": brand["description"]
                })
                continue

            # 2️⃣ Fuzzy match
            for kw in keywords:
                if get_close_matches(part, [kw], cutoff=0.7):
                    found_brands.append({
                        "brand": brand["brand_name"],
                        "url": brand["web_link"],
                        "match_type": "fuzzy",
                        "matched_with": part,
                        "description": brand["description"]
                    })
                    break

    # Remove duplicates (by brand name)
    unique_brands = []
    seen = set()
    for b in found_brands:
        if b["brand"] not in seen:
            unique_brands.append(b)
            seen.add(b["brand"])

    if not unique_brands:
        return {
            "status": "no_match",
            "message": "No matching brands found for your query."
        }

    return {
        "status": "success",
        "total_matches": len(unique_brands),
        "brands": unique_brands
    }

# ------------------------------------------------------------------------------
# Run MCP server
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
