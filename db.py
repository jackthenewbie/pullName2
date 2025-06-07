import redis
from config import redis_name, redis_password, redis_host
db = redis.Redis(
    host=redis_host,
    port=11954,
    decode_responses=True,
    username=redis_name,
    password=redis_password
)
