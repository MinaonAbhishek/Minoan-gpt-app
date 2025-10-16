from fastmcp import FastMCP
import os
import aiosqlite
import tempfile
import json
from datetime import datetime

# Use temporary directory which should be writable
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "minoan.db")

print(f"Database path: {DB_PATH}")

mcp = FastMCP("Minoan")

def init_db():
    """Initialize the Minoan product database with furniture and décor product names"""
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            
            # Create simple products table with just names
            c.execute("""
                CREATE TABLE IF NOT EXISTS products(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            
            # Check if we need to seed data
            cursor = c.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Seed sample furniture and décor product names
                sample_products = [
                    ("Modern Velvet Sofa",),
                    ("Scandinavian Dining Table",),
                    ("Industrial Floor Lamp",),
                    ("Bohemian Area Rug",),
                    ("Mid-Century Armchair",),
                    ("Marble Coffee Table",),
                    ("Ceramic Vase Set",),
                    ("Platform Bed Frame",),
                    ("Rattan Pendant Light",),
                    ("Abstract Wall Art",)
                ]
                
                c.executemany("""
                    INSERT INTO products(name) VALUES (?)
                """, sample_products)
                
                c.commit()
                print(f"Database initialized with {len(sample_products)} sample products")
            else:
                print(f"Database already contains {count} products")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

# Initialize database synchronously at module load
init_db()

@mcp.tool()
async def get_products():
    """Fetch all furniture and décor products from the Minoan catalog."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute("SELECT id, name FROM products ORDER BY name")
            products = []
            async for row in cur:
                products.append({
                    "id": row[0],
                    "name": row[1]
                })
            
            return {
                "status": "success",
                "count": len(products),
                "products": products
            }
    except Exception as e:
        return {"status": "error", "message": f"Error fetching products: {str(e)}"}

@mcp.resource("minoan:///catalog", mime_type="application/json")
def product_catalog():
    """Provide the full product catalog as a resource."""
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute("SELECT id, name FROM products ORDER BY name")
            products = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
            
            catalog = {
                "store": "Minoan",
                "description": "Discover and purchase furniture and décor through natural conversation",
                "total_products": len(products),
                "products": products
            }
            
            return json.dumps(catalog, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Could not load catalog: {str(e)}"}, indent=2)

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)