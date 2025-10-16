# Minoan - AI-Powered Furniture Shopping

Minoan is a shopping application that runs inside ChatGPT via the Model Context Protocol (MCP). Users can discover and purchase furniture and décor through natural conversation.

## Features

- **Simple Product Catalog**: Browse furniture and décor product names
- **MCP Integration**: Easy integration with ChatGPT via MCP
- **Async Database**: Fast async operations with aiosqlite

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

## MCP Tool

### `get_products`
Fetch all furniture and décor products from the Minoan catalog.

**Returns:**
```json
{
  "status": "success",
  "count": 10,
  "products": [
    {"id": 1, "name": "Modern Velvet Sofa"},
    {"id": 2, "name": "Scandinavian Dining Table"},
    ...
  ]
}
```

**Example Usage in ChatGPT:**
- "Show me all furniture products"
- "What products do you have?"
- "List all items in the catalog"

## MCP Resource

### `minoan:///catalog`
Access the full product catalog as a JSON resource.

Returns a structured catalog with store information and all products.

## Sample Products

The catalog includes 10 furniture and décor items:

1. Modern Velvet Sofa
2. Scandinavian Dining Table
3. Industrial Floor Lamp
4. Bohemian Area Rug
5. Mid-Century Armchair
6. Marble Coffee Table
7. Ceramic Vase Set
8. Platform Bed Frame
9. Rattan Pendant Light
10. Abstract Wall Art

## Database

Simple SQLite database with one table:

### Products Table
- `id`: Product ID (auto-increment)
- `name`: Product name (text)

Database location: System temp directory (`/tmp/minoan.db` on macOS/Linux)

## Architecture

- **Framework**: FastMCP (Model Context Protocol)
- **Database**: SQLite with async operations (aiosqlite)
- **Transport**: HTTP on port 8000
- **Server**: Uvicorn ASGI server

## Deployment

Ready for deployment to FastMCP Cloud or any MCP-compatible platform:

1. All dependencies are in `pyproject.toml`
2. Simple, lightweight design
3. No external API dependencies

```bash
git add .
git commit -m "Minoan furniture shopping app"
git push
```

## Development

- Database auto-initializes on first run
- Products are seeded automatically
- Clean async/await pattern throughout

## License

MIT License
