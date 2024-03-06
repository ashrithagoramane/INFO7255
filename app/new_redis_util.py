import os

import redis
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest

load_dotenv()

HOST = os.getenv("REDIS_SERVER_HOST", "localhost")
PORT = os.getenv("REDIS_SERVER_PORT", 6379)

r = redis.Redis(host=HOST, port=PORT, decode_responses=True)

def set(key: str, value: str):
    print(f"Adding {key}")
    r.set(key, value)

def hset(key: str, value: dict):
    print(f"Adding {key}")
    r.hset(key, mapping=value)

def sadd(key: str, value: str):
    print(f"Adding {key}")
    r.sadd(key, value)
