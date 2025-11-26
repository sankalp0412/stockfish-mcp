# flake8: noqa
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from stockfish import Stockfish, StockfishException
from .models.game import Game
from .database import get_redis_client, save_game_to_redis, get_game_by_game_id, delete_game_by_game_id
from PIL import Image
import requests

load_dotenv()
userdata = os.environ
STOCKFISH_PATH = userdata.get("STOCKFISH_PATH")
mcp = FastMCP("stockfish")

redis_client = get_redis_client()


@mcp.tool()
async def get_best_moves(game_id: str) -> list | str:
    """
    Asynchronously calculates the best moves for a given chess position using the Stockfish engine.

    Args:
        fen (str): The FEN (Forsyth-Edwards Notation) string representing the current chessboard state.
        user_elo_rating (int | str): The ELO rating of the user, which can be used to adjust the engine's playing strength, default being 3000 elo.

    Returns:
        list: A list of the best moves suggested by the Stockfish engine for the given position.
    """
    game = get_game_by_game_id(game_id=game_id, redis_client=redis_client)
    user_elo = game.get_elo()
    current_fen = game.get_fen()
    stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"UCI_Elo": user_elo})

    try:
        if not stockfish.is_fen_valid(current_fen):
            return "The input fen String is invalid"

        stockfish.set_fen_position(current_fen)
        res = stockfish.get_top_moves(3)

        return res
    except StockfishException as se:
        return f"Exception while finding top moves:{se}"


@mcp.tool()
async def start_game(user_elo: int | str = 3000) -> str:
    """
    Initializes a new chess game with the specified user ELO rating and returns the newly created game_id string.

    Args:
        user_elo (int | str): The ELO rating of the user, default being 3000 (max).

    Returns:
        str: The unique identifier of the newly created uuid in string.
    """
    try:
        new_game = Game(user_elo=str(user_elo))
        game_id = new_game.get_game_id()
        success = save_game_to_redis(game_id=game_id, game=new_game, redis_client=redis_client)
        if success:
            return game_id
    except Exception as e:
        return f"Error while starting game: {e}"



@mcp.tool()
async def get_board_visual(game_id: str) -> ImageContent | str:
    """
    Generates a visual representation of the current chess board position.
    
    Args:
        game_id (str): The unique identifier of the game.
    
    Returns:
        ImageContent: Board Visual
    """
    base_url = "https://fen2image.chessvision.ai/"
    game = get_game_by_game_id(game_id=game_id, redis_client=redis_client)
    if game is None:
        return "Game not found"
    
    current_fen = game.get_fen()
    image_url = base_url + current_fen
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Convert image to base64
        img = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return ImageContent(
            type="image",
            data=img_base64,
            mimeType="image/png"
        )
    except requests.RequestException as e:
        return f"Error fetching board image: {e}"
    except Exception as e:
        return f"Error processing image: {e}"
    
    
    
    

@mcp.tool()
async def play_move(game_id: str, user_move: str) -> bool:
    """
    Validates and applies a chess move to the game state, then updates the database.
    
    IMPORTANT: This function must be called TWICE per turn:
    1. First, after the user makes their move to update the game state
    2. Second, after selecting and making the AI's response move from get_best_moves
    
    Both the user's moves and AI's moves must be played through this function to keep 
    the game state synchronized in the database.

    Args:
        game_id (str): The unique identifier of the game.
        user_move (str): The move in standard UCI chess notation (e.g., 'e2e4', 'g1f3'). 
                        Can be either a user move or an AI-selected move.

    Returns:
        bool: True if the move is valid and the game state is updated, False otherwise.
    """
    game = get_game_by_game_id(game_id=game_id, redis_client=redis_client)
    if game is None:
        return False

    previous_fen = game.get_fen()
    previous_moves = game.moves.copy()

    if not game.play_move(user_move):
        return False

    if save_game_to_redis(game_id=game_id, game=game, redis_client=redis_client):
        return True

    game.fen = previous_fen
    game.moves = previous_moves
    return False


@mcp.tool()
async def close_game(game_id: str) -> bool:
    """
    Closes an ongoing chess game by removing its associated data from the Redis database.

    Args:
        game_id (str): The unique identifier of the game to be closed.
    Returns:
        bool: True if the game was successfully closed, False otherwise.
    """
    try:
        deleted = delete_game_by_game_id(game_id=game_id, redis_client=redis_client)
        return bool(deleted)
    except Exception as e:
        print(f"Error while closing game: {e}")
        return False


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
