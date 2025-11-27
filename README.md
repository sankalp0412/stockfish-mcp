# Stockfish MCP Server

A Model Context Protocol (MCP) server that integrates the Stockfish chess engine with Claude Desktop, allowing you to play chess with AI assistance.

## Features

- 🎮 Start and manage chess games with customizable ELO ratings
- 🤖 Get best move suggestions from Stockfish engine
- 📊 Persistent game state storage using Redis
- ♟️ Full UCI chess notation support
- 🔄 Real-time game state updates
- 🖼️ Visual board representation with auto-generated images

## Prerequisites

- Python 3.13+
- [Stockfish Chess Engine](https://stockfishchess.org/download/)
- Redis Server
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sankalp0412/stockfish-mcp.git
cd stockfish-mcp
```

### 2. Install Stockfish

**macOS (Homebrew):**
```bash
brew install stockfish
which stockfish  # Note the path for later
```

**Linux:**
```bash
sudo apt-get install stockfish  # Debian/Ubuntu
# or
sudo yum install stockfish      # RHEL/CentOS
```

**Windows:**
Download from [stockfishchess.org/download](https://stockfishchess.org/download/)

### 3. Install Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows:**
Use [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your Stockfish path:
```env
STOCKFISH_PATH=/usr/local/bin/stockfish  # Update with your actual path
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 5. Install Python Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
```

## Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stockfish-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/stockfish-mcp",
        "run",
        "stockfish-mcp"
      ]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/stockfish-mcp` with the actual absolute path to your cloned repository.

**Restart Claude Desktop** completely (quit and reopen) for changes to take effect.

## Usage

Once configured, you can interact with the chess engine through Claude. Here's how to play:

### Start a New Game
```
Start a chess game with ELO rating 2000
```

### Play Chess
Simply tell Claude your moves in natural language:
```
I want to play e4
Play knight to f3
Move my bishop to c4
```

Claude will:
- Use `play_move` to apply your move
- Use `get_best_moves` internally to analyze the position
- Select and play its response move
- Keep the game state updated in the database

### View the Board
```
Show me the current board position
```

Claude will display a visual representation of the chess board at any point in the game.

### Close a Game
```
Close the game
```

**Note:** The `get_best_moves` tool is used by Claude itself to analyze positions and decide its moves. You don't need to call it directly - just play naturally!

## MCP Tools Reference

| Tool | Description | Parameters |
|------|-------------|------------|
| `start_game` | Initialize a new chess game | `user_elo` (optional, default: 3000) |
| `get_best_moves` | Get top 3 moves for current position | `game_id` |
| `play_move` | Validate and apply a move | `game_id`, `user_move` (UCI notation) |
| `get_board_visual` | Generate visual board representation | `game_id` |
| `close_game` | End game and remove from database | `game_id` |


### MCP Server Not Showing in Claude

1. Check Claude Desktop logs for errors
2. Verify absolute paths in `claude_desktop_config.json`
3. Ensure Redis is running: `redis-cli ping` (should return `PONG`)
4. Verify Stockfish path: `$STOCKFISH_PATH --version`
5. Restart Claude Desktop completely

### Import Errors

```bash
cd /path/to/stockfish-mcp
uv sync  # Reinstall dependencies
```

### Redis Connection Errors

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## Author

Sankalp Dhupar ([@sankalp0412](https://github.com/sankalp0412))

## Acknowledgments

- [Stockfish Chess Engine](https://stockfishchess.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Claude](https://www.anthropic.com/)
