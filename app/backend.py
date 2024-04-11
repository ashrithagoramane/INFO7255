import redis_util as redis_util
from werkzeug.exceptions import BadRequest, NotFound
import rabbitmq_util

OBJECT_TYPE = "objectType"
OBJECT_ID = "objectId"
INVERSE_KEYWORD = "INVERSE"

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
        redisKey = f"{object_type}:{object_id}"
        if not redis_util.exists(redisKey):
            raise BadRequest(f"{object_type} with id {object_id} not present")
        return getObject(f"{object_type}:{object_id}", delete=True)
    else:
        return_objects = []
        all_object_keys = redis_util.get_keys(f"{object_type}:*")
        for key in all_object_keys:
            if len(key.split(":")) != 2:
                continue
            return_objects.append(getObject(key, delete=True))
        return return_objects


def patch_object(object_type: str, object_id: str, object: dict = {}):
    redisKey = f"{object_type}:{object_id}"
    if not redis_util.exists(redisKey):
        raise BadRequest(f"{object_type} with id {object_id} not present")
    processObject(object)
    return object


def processList(objects: list = [], parent: str = None, child_type: str = None):
    return_list = []

    for item in objects:
        if isinstance(item, dict):
            value = str(processObject(item, parent, child_type))
        elif isinstance(item, list):
            pass
        else:
            value = str(item)
        return_list.append(value)

    return return_list


def processObject(object: dict = {}, parent: str = None, child_type: str = None):
    redisKey = f"{object.get(OBJECT_TYPE)}:{object.get(OBJECT_ID)}"

    simple_values = {}
    for attribute, value in object.items():
        if isinstance(value, dict):
            object_redis_key = processObject(value, object.get(OBJECT_ID), attribute)
            # Add link of sub object to current object
            redis_sub_key = f"{redisKey}::{attribute}"
            redis_util.set(redis_sub_key, object_redis_key)
            
            # Add inverse link
            redis_util.sadd(f"{object_redis_key}::{INVERSE_KEYWORD}", redisKey)
        elif isinstance(value, list):
            processed_list = processList(value, object.get(OBJECT_ID), attribute)
            # Add values to set (list of linked objects)
            for val in processed_list:
                redis_sub_key = f"{redisKey}::{attribute}"
                redis_util.sadd(redis_sub_key, val)
                
                # Add inverse of link
                redis_util.sadd(f"{val}::{INVERSE_KEYWORD}", redisKey)
        else:
            simple_values[attribute] = str(value)

    redis_util.hset(redisKey, simple_values)
    process_and_push_to_queue(simple_values, parent, child_type)
    return redisKey


def getObject(redisKey: str, delete: bool = False, parent: str = None, maxCard: int = 0):
    object = {}
    
    if not redis_util.exists(redisKey):
        raise NotFound(f"{redisKey} not found in database")
    
    all_keys = redis_util.get_keys(f"{redisKey}*")

    if parent and delete and maxCard < 1:
        # Removing parent from inverse list only of any of it's parent 
        # is not linked with an object
        redis_util.srem(f"{redisKey}::{INVERSE_KEYWORD}", parent)

    maxCard = max(redis_util.scard(f"{redisKey}::{INVERSE_KEYWORD}"), maxCard)

    for key in all_keys:
        if key == redisKey:
            simple_values = redis_util.hgetall(key)
            object.update(simple_values)
        elif key.startswith(f"{redisKey}::{INVERSE_KEYWORD}"):
            continue
        elif key.startswith(f"{redisKey}::"):
            if redis_util.get_type(key) == "string":
                object[key.split("::")[-1]] = getObject(redis_util.get(key), delete, redisKey, maxCard)
            elif redis_util.get_type(key) == "set":
                set_members = redis_util.smembers(key)
                object[key.split("::")[-1]] = [
                    getObject(sub_key, delete, redisKey, maxCard) for sub_key in set_members
                ]
        else:
            if delete:
                all_keys.remove(key)

    if delete and redis_util.is_set_empty(f"{redisKey}::{INVERSE_KEYWORD}"):
        # If object is not linked in any parent object delete it's corresponding keys
        redis_util.delete_keys(all_keys)

    return object


def process_and_push_to_queue(data, parent_id, child_type):
    data["plan_join"] = dict()
    if parent_id:
        data["plan_join"]["name"] = child_type
        data["plan_join"]["parent"] = parent_id
    elif data.get(OBJECT_TYPE) in ["plan", "planservice"]:
        if data.get(OBJECT_TYPE) == "planservice":
            data["plan_join"]["name"] = "linkedPlanServices"
        else:
            data["plan_join"]["name"] = data.get(OBJECT_TYPE)
    print(data)
    rabbitmq_util.push_to_queue(data)
