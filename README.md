# Minoan - AI-Powered Furniture Shopping

Minoan is a shopping application that runs inside ChatGPT via the Model Context Protocol (MCP). Users can discover, configure, and purchase furniture and décor through natural conversation—text and images—without leaving the chat.

## Features

- **Natural Conversation**: Shop for furniture using natural language
- **Product Discovery**: Search and browse furniture and décor items
- **Detailed Product Info**: Get comprehensive details about products
- **Simple Ordering**: Create orders directly through conversation
- **Category Browsing**: Explore products by category

## Quick Start

### Prerequisites

- Python 3.13+
- `uv` package manager

### Installation

```bash
# Install dependencies
uv sync

# Run the server
uv run main.py
```

The server will start on `http://0.0.0.0:8000/mcp`

### Testing

Run the test suite to verify functionality:

```bash
uv run test_minoan.py
```

## MCP Tools

The Minoan MCP server provides the following tools:

### `search_products`
Search for furniture and décor products by keyword, category, and price range.

**Parameters:**
- `query` (string, optional): Search term to match against product name or description
- `category` (string, optional): Filter by category (e.g., "Living Room", "Bedroom", "Lighting", "Décor")
- `max_price` (float, optional): Maximum price filter
- `min_price` (float, optional): Minimum price filter

**Example:**
```
search_products(query="sofa", category="Living Room", max_price=2000)
```

### `get_product_details`
Get detailed information about a specific product by ID.

**Parameters:**
- `product_id` (int): ID of the product

**Example:**
```
get_product_details(product_id=1)
```

### `list_categories`
Get all available product categories.

**Example:**
```
list_categories()
```

### `create_order`
Create an order for a product.

**Parameters:**
- `product_id` (int): ID of the product to order
- `quantity` (int, default: 1): Number of items to order
- `customer_name` (string, optional): Customer's name
- `customer_email` (string, optional): Customer's email

**Example:**
```
create_order(product_id=1, quantity=2, customer_name="John Doe", customer_email="john@example.com")
```

## MCP Resources

### `minoan:///catalog`
Access the full product catalog as a JSON resource.

## Product Categories

- **Living Room**: Sofas, armchairs, coffee tables
- **Bedroom**: Beds, nightstands, dressers
- **Dining Room**: Dining tables, chairs
- **Lighting**: Floor lamps, pendant lights, chandeliers
- **Décor**: Vases, wall art, decorative objects
- **Rugs & Textiles**: Area rugs, throws, pillows

## Database

The application uses SQLite with the following tables:

### Products Table
- `id`: Product ID
- `name`: Product name
- `description`: Detailed product description
- `category`: Product category
- `price`: Price in USD
- `in_stock`: Stock availability (1 = in stock, 0 = out of stock)
- `dimensions`: Product dimensions
- `material`: Materials used
- `color`: Color(s)
- `image_url`: Product image URL

### Orders Table
- `id`: Order ID
- `product_id`: Foreign key to products
- `quantity`: Number of items ordered
- `customer_name`: Customer name
- `customer_email`: Customer email
- `order_date`: ISO format datetime
- `status`: Order status (pending, confirmed, shipped, delivered)

## Sample Products

The database is pre-seeded with 10 furniture and décor items including:

- Modern Velvet Sofa ($1,299.99)
- Scandinavian Dining Table ($899.99)
- Industrial Floor Lamp ($189.99)
- Bohemian Area Rug ($349.99)
- Mid-Century Armchair ($699.99)
- Marble Coffee Table ($549.99)
- Ceramic Vase Set ($79.99)
- Platform Bed Frame ($899.99)
- Rattan Pendant Light ($159.99)
- Abstract Wall Art ($249.99)

## Architecture

- **Framework**: FastMCP (Model Context Protocol)
- **Database**: SQLite with async operations (aiosqlite)
- **Transport**: HTTP on port 8000
- **Server**: Uvicorn ASGI server

## Deployment

The application is deployment-ready for FastMCP Cloud or any MCP-compatible platform:

1. Ensure all dependencies are in `pyproject.toml`
2. Commit changes to git
3. Deploy to your preferred platform

```bash
git add .
git commit -m "Minoan furniture shopping app"
git push
```

## Development

The database file is stored in the system's temporary directory:
- macOS/Linux: `/tmp/minoan.db`
- Windows: `%TEMP%\minoan.db`

## Future Enhancements

- Image recognition for visual search
- Product recommendations based on preferences
- Shopping cart functionality
- Multiple payment methods
- User authentication
- Order tracking and history
- Product reviews and ratings
- Customization options (colors, materials, sizes)
- 3D product previews
- AR furniture placement

## License

MIT License

