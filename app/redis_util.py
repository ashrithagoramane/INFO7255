import redis
from dotenv import load_dotenv
import os
import json

load_dotenv()

HOST = os.getenv("REDIS_SERVER_HOST", "localhost")
PORT = os.getenv("REDIS_SERVER_PORT", 6379)

r = redis.Redis(host=HOST, port=PORT, decode_responses=True)

def create_plan(json_data):
    key = f'{json_data.get("objectId")}'
    r.set(key, json.dumps(json_data))
    return json_data

def get_plan(plan_id=None):
    if plan_id:
        plan = json.loads(r.get(f'{plan_id}'))
        return plan
    plans = [json.loads(r.get(key)) for key in r.keys()]
    return plans

def delete_plan(plan_id):
    r.delete(f'{plan_id}')
