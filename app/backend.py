import redis_util as redis_util
from werkzeug.exceptions import BadRequest

OBJECT_TYPE = "objectType"
OBJECT_ID = "objectId"


def insert_object(object: dict = {}):
    redisKey = f"{object.get(OBJECT_TYPE)}:{object.get(OBJECT_ID)}"
    if redis_util.exists(redisKey):
        raise BadRequest(f"Object already exists. Key: {redisKey}")
    processObject(object)
    return object


def get_object(object_type: str, object_id: str = None):
    if object_id:
        return getObject(f"{object_type}:{object_id}")
    else:
        return_objects = []
        all_object_keys = redis_util.get_keys(f"{object_type}:*")
        for key in all_object_keys:
            if len(key.split(":")) != 2:
                continue
            return_objects.append(getObject(key))
        return return_objects


def delete_object(object_type: str, object_id: str = None):
    if object_id:
        return getObject(f"{object_type}:{object_id}", delete=True)
    else:
        return_objects = []
        all_object_keys = redis_util.get_keys(f"{object_type}:*")
        for key in all_object_keys:
            if len(key.split(":")) != 2:
                continue
            return_objects.append(getObject(key, delete=True))
        return return_objects

def patch_object(object: dict = {}):
    processObject(object)
    return object

def processList(objects: list = []):
    return_list = []

    for item in objects:
        if isinstance(item, dict):
            value = str(processObject(item))
        elif isinstance(item, list):
            pass
        else:
            value = str(item)
        return_list.append(value)

    return return_list


def processObject(object: dict = {}):
    redisKey = f"{object.get(OBJECT_TYPE)}:{object.get(OBJECT_ID)}"

    simple_values = {}
    for attribute, value in object.items():
        if isinstance(value, dict):
            object_redis_key = processObject(value)
            # Add link of sub object to current object
            redis_sub_key = f"{redisKey}::{attribute}"
            redis_util.set(redis_sub_key, object_redis_key)
        elif isinstance(value, list):
            processed_list = processList(value)
            # Add values to set (list of linked objects)
            for val in processed_list:
                redis_sub_key = f"{redisKey}::{attribute}"
                redis_util.sadd(redis_sub_key, val)
        else:
            simple_values[attribute] = str(value)

    redis_util.hset(redisKey, simple_values)

    return redisKey


def getObject(redisKey: str, delete: bool = False):
    object = {}

    all_keys = redis_util.get_keys(f"{redisKey}*")

    for key in all_keys:
        if key == redisKey:
            simple_values = redis_util.hgetall(key)
            object.update(simple_values)
        else:
            if redis_util.get_type(key) == "string":
                object[key.split("::")[-1]] = getObject(redis_util.get(key))
            elif redis_util.get_type(key) == "set":
                set_members = redis_util.smembers(key)
                object[key.split("::")[-1]] = [
                    getObject(sub_key) for sub_key in set_members
                ]
    if delete:
        redis_util.delete_keys(all_keys)

    return object
