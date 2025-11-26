import redis
from redis import Redis


def get_redis_client() -> Redis:

    try:
        r = Redis(host="localhost", port=6379, decode_responses=False)
        r.ping()
        return r
    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        raise