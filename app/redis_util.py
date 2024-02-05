import redis
from dotenv import load_dotenv
import os
import json

load_dotenv()

HOST = os.getenv("REDIS_SERVER_HOST", "localhost")
PORT = os.getenv("REDIS_SERVER_PORT", 6379)

r = redis.Redis(host=HOST, port=PORT, decode_responses=True)

def create_plan(json_data):
    key = f'{json_data.get("objectType")}:{json_data.get("objectId")}'
    r.set(key, json.dumps(json_data))

# data = {

# 	"planCostShares": {
# 		"deductible": 2000,
# 		"_org": "example.com",
# 		"copay": 23,
# 		"objectId": "1234vxc2324sdf-501",
# 		"objectType": "membercostshare"
		
# 	},
# 	"linkedPlanServices": [{
# 		"linkedService": {
# 			"_org": "example.com",
# 			"objectId": "1234520xvc30asdf-502",
# 			"objectType": "service",
# 			"name": "Yearly physical"
# 		},
# 		"planserviceCostShares": {
# 			"deductible": 10,
# 			"_org": "example.com",
# 			"copay": 0,
# 			"objectId": "1234512xvc1314asdfs-503",
# 			"objectType": "membercostshare"
# 		},
# 		"_org": "example.com",
# 		"objectId": "27283xvx9asdff-504",
# 		"objectType": "planservice"
# 	}, {
# 		"linkedService": {
# 			"_org": "example.com",
# 			"objectId": "1234520xvc30sfs-505",
# 			"objectType": "service",
# 			"name": "well baby"
# 		},
# 		"planserviceCostShares": {
# 			"deductible": 10,
# 			"_org": "example.com",
# 			"copay": 175,
# 			"objectId": "1234512xvc1314sdfsd-506",
# 			"objectType": "membercostshare"
# 		},
		
# 		"_org": "example.com",
		
# 		"objectId": "27283xvx9sdf-507",
# 		"objectType": "planservice"
# 	}],


# 	"_org": "example.com",
# 	"objectId": "12xvxc345ssdsds-508",
# 	"objectType": "plan",
# 	"planType": "inNetwork",
# 	"creationDate": "12-12-2017"
# }
# create_plan(data)
