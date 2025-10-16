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
    """Initialize the Minoan product database with sample furniture and décor items"""
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            
            # Create products table
            c.execute("""
                CREATE TABLE IF NOT EXISTS products(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    in_stock INTEGER DEFAULT 1,
                    dimensions TEXT,
                    material TEXT,
                    color TEXT,
                    image_url TEXT
                )
            """)
            
            # Create orders table
            c.execute("""
                CREATE TABLE IF NOT EXISTS orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    customer_name TEXT,
                    customer_email TEXT,
                    order_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Check if we need to seed data
            cursor = c.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Seed sample furniture and décor products
                sample_products = [
                    ("Modern Velvet Sofa", "Luxurious 3-seater sofa with velvet upholstery and solid wood legs", "Living Room", 1299.99, 1, "85\" W x 36\" D x 33\" H", "Velvet, Wood", "Navy Blue", "https://example.com/sofa.jpg"),
                    ("Scandinavian Dining Table", "Minimalist oak dining table with clean lines, seats 6-8 people", "Dining Room", 899.99, 1, "72\" L x 36\" W x 30\" H", "Oak Wood", "Natural", "https://example.com/table.jpg"),
                    ("Industrial Floor Lamp", "Adjustable floor lamp with metal frame and Edison bulb", "Lighting", 189.99, 1, "65\" H", "Metal, Brass", "Black", "https://example.com/lamp.jpg"),
                    ("Bohemian Area Rug", "Hand-woven geometric pattern rug with fringe details", "Rugs & Textiles", 349.99, 1, "8' x 10'", "Cotton, Jute", "Multi-color", "https://example.com/rug.jpg"),
                    ("Mid-Century Armchair", "Iconic design with tufted leather seat and walnut frame", "Living Room", 699.99, 1, "32\" W x 34\" D x 31\" H", "Leather, Walnut", "Cognac Brown", "https://example.com/armchair.jpg"),
                    ("Marble Coffee Table", "Round coffee table with white marble top and gold base", "Living Room", 549.99, 1, "36\" Diameter x 18\" H", "Marble, Metal", "White/Gold", "https://example.com/coffee-table.jpg"),
                    ("Ceramic Vase Set", "Set of 3 handcrafted ceramic vases in varying heights", "Décor", 79.99, 1, "6\", 8\", 10\" H", "Ceramic", "Matte White", "https://example.com/vases.jpg"),
                    ("Platform Bed Frame", "Low-profile king bed with upholstered headboard", "Bedroom", 899.99, 1, "80\" W x 86\" L x 45\" H", "Wood, Linen", "Gray", "https://example.com/bed.jpg"),
                    ("Rattan Pendant Light", "Natural woven pendant with adjustable cord", "Lighting", 159.99, 1, "16\" Diameter", "Rattan", "Natural", "https://example.com/pendant.jpg"),
                    ("Abstract Wall Art", "Modern canvas print with gold leaf accents, framed", "Décor", 249.99, 1, "36\" x 48\"", "Canvas, Wood Frame", "Blue/Gold", "https://example.com/art.jpg")
                ]
                
                c.executemany("""
                    INSERT INTO products(name, description, category, price, in_stock, dimensions, material, color, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
async def search_products(query: str = "", category: str = "", max_price: float = None, min_price: float = None):
    """Search for furniture and décor products by keyword, category, and price range.
    
    Args:
        query: Search term to match against product name or description
        category: Filter by category (e.g., "Living Room", "Bedroom", "Lighting", "Décor")
        max_price: Maximum price filter
        min_price: Minimum price filter
    """
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            sql = "SELECT * FROM products WHERE in_stock = 1"
            params = []
            
            if query:
                sql += " AND (name LIKE ? OR description LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if min_price is not None:
                sql += " AND price >= ?"
                params.append(min_price)
            
            if max_price is not None:
                sql += " AND price <= ?"
                params.append(max_price)
            
            sql += " ORDER BY name"
            
            cur = await c.execute(sql, params)
            cols = [d[0] for d in cur.description]
            products = [dict(zip(cols, r)) for r in await cur.fetchall()]
            
            return {
                "status": "success",
                "count": len(products),
                "products": products
            }
    except Exception as e:
        return {"status": "error", "message": f"Error searching products: {str(e)}"}

@mcp.tool()
async def get_product_details(product_id: int):
    """Get detailed information about a specific product by ID."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            )
            cols = [d[0] for d in cur.description]
            row = await cur.fetchone()
            
            if row:
                product = dict(zip(cols, row))
                return {
                    "status": "success",
                    "product": product
                }
            else:
                return {
                    "status": "error",
                    "message": f"Product with ID {product_id} not found"
                }
    except Exception as e:
        return {"status": "error", "message": f"Error getting product details: {str(e)}"}

@mcp.tool()
async def list_categories():
    """Get all available product categories."""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "SELECT DISTINCT category FROM products ORDER BY category"
            )
            categories = [row[0] for row in await cur.fetchall()]
            
            return {
                "status": "success",
                "categories": categories
            }
    except Exception as e:
        return {"status": "error", "message": f"Error listing categories: {str(e)}"}

@mcp.tool()
async def create_order(product_id: int, quantity: int = 1, customer_name: str = "", customer_email: str = ""):
    """Create an order for a product.
    
    Args:
        product_id: ID of the product to order
        quantity: Number of items to order (default: 1)
        customer_name: Customer's name (optional)
        customer_email: Customer's email (optional)
    """
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            # Check if product exists and is in stock
            cur = await c.execute(
                "SELECT name, price, in_stock FROM products WHERE id = ?",
                (product_id,)
            )
            product = await cur.fetchone()
            
            if not product:
                return {
                    "status": "error",
                    "message": f"Product with ID {product_id} not found"
                }
            
            product_name, price, in_stock = product
            
            if not in_stock:
                return {
                    "status": "error",
                    "message": f"Product '{product_name}' is currently out of stock"
                }
            
            # Create order
            order_date = datetime.now().isoformat()
            cur = await c.execute(
                """INSERT INTO orders(product_id, quantity, customer_name, customer_email, order_date, status)
                   VALUES (?, ?, ?, ?, ?, 'pending')""",
                (product_id, quantity, customer_name, customer_email, order_date)
            )
            order_id = cur.lastrowid
            await c.commit()
            
            total_price = price * quantity
            
            return {
                "status": "success",
                "order_id": order_id,
                "message": f"Order created successfully for {quantity}x {product_name}",
                "total_price": total_price,
                "order_details": {
                    "order_id": order_id,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": price,
                    "total_price": total_price,
                    "order_date": order_date,
                    "status": "pending"
                }
            }
    except Exception as e:
        return {"status": "error", "message": f"Error creating order: {str(e)}"}

@mcp.resource("minoan:///catalog", mime_type="application/json")
def product_catalog():
    """Provide the full product catalog as a resource."""
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            cur = c.execute("""
                SELECT id, name, description, category, price, in_stock, 
                       dimensions, material, color
                FROM products
                WHERE in_stock = 1
                ORDER BY category, name
            """)
            cols = [d[0] for d in cur.description]
            products = [dict(zip(cols, row)) for row in cur.fetchall()]
            
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