import new_redis_util as redis_util

OBJECT_TYPE = "objectType"
OBJECT_ID = "objectId"

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
