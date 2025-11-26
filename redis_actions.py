from redis import Redis
from games import Game
import pickle
from common import get_redis_client

def save_game_to_redis(game_id: str, game: Game, redis_client:Redis ) -> bool:
    try:
        serialized_game= pickle.dumps(game,protocol=pickle.HIGHEST_PROTOCOL)
        redis_client.set(game_id, serialized_game)
        return True
    except Exception as e:
        print(f"An error occurred while saving the game to Redis: {e}")
        return False
 
def get_game_by_game_id(game_id: str, redis_client: Redis) -> Game:
    try:
        data: Game = redis_client.get(game_id)
        if data:
            game = pickle.loads(data)
            return game
        else:
            return None
    except Exception as e:
        print(f"Error while getting game from Redis: {e}")
        
      
def delete_game_by_game_id(game_id: str, redis_client: Redis) -> bool:
    try :
        redis_client.delete(game_id)
        return True
    except Exception as e:
        print(f"Error while deleting game: {e}")
        return False

if __name__ == "__main__":
    pass