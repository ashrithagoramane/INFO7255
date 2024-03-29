import json
import os

import redis
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest, NotFound

load_dotenv()

HOST = os.getenv("REDIS_SERVER_HOST", "localhost")
PORT = os.getenv("REDIS_SERVER_PORT", 6379)

r = redis.Redis(host=HOST, port=PORT, decode_responses=True)


def create(json_data):
    key = f'{json_data.get("objectType")}:{json_data.get("objectId")}'
    if r.exists(key):
        raise BadRequest(f"{key} already exists")
    r.set(key, json.dumps(json_data))
    return json_data


def get(objectType=None, objectId=None):
    if objectType and objectId:
        key = f"{objectType}:{objectId}"
        if not r.exists(key):
            raise NotFound
        object = json.loads(r.get(key))
        return object
    objects = [json.loads(r.get(key)) for key in r.keys()]
    return objects


def delete(objectType, objectId):
    key = f"{objectType}:{objectId}"
    if objectType and objectId:
        if not r.exists(key):
            raise NotFound
    r.delete(key)
