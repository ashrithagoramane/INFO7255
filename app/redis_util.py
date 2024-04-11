import os

import redis
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("REDIS_SERVER_HOST", "localhost")
PORT = os.getenv("REDIS_SERVER_PORT", 6379)
queue_name = os.getenv("QUEUE_NAME", "indexing_queue")
r = redis.Redis(host=HOST, port=PORT, decode_responses=True)


def set(key: str, value: str):
    r.set(key, value)


def hset(key: str, value: dict):
    r.hset(key, mapping=value)


def sadd(key: str, value: str):
    r.sadd(key, value)


def get_keys(pattern: str):
    return r.keys(pattern)


def hgetall(key: str):
    values = r.hgetall(key)
    for k,v  in values.items():
        try:
            values[k] = int(v)
        except ValueError:
            pass
    return values




def get_type(key: str):
    return r.type(key)


def get(key: str):
    return r.get(key)


def smembers(key: str):
    return r.smembers(key)

def srem(key: str, member: str):
    if r.sismember(key, member):
        r.srem(key, member)

def is_set_empty(key: str):
    if r.scard(key):
        return False
    return True

def scard(key: str):
    if r.exists(key):
        return r.scard(key)
    return 0

def delete_keys(keys: list):
    if not keys:
        return
    r.delete(*keys)


def exists(key: str):
    return r.exists(key)
