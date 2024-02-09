import json
import logging

import redis_util
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_expects_json import expects_json
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.http import generate_etag

load_dotenv()

VERSION = "/v1"

logging.basicConfig(filename='app.log', level=logging.DEBUG)
schema = json.load(open('./schemas/plan_schema.json'))
app = Flask(__name__)

@app.route(VERSION + '/health', methods=["GET"])
def check_health():
    """
    Route to check health of the application
    """
    app.logger.info("Health request handled successfully")
    return jsonify({'message': 'Application is healthy!'}), 200

@app.route(VERSION + '/plan', methods=['POST'])
@expects_json(schema=schema)
def create_plan():
    """
    Create a plan
    """
    try:
        app.logger.info("Handling create plan request")
        request_data = request.get_json()
        response_data = redis_util.create(request_data)
        etag = generate_etag(json.dumps(response_data).encode())
    except BadRequest as e:
        return {'message': f'{str(e)}'}, 400
    except Exception as e:
        return {'message': 'Invalid request JSON. Failed to create user'}, 400
    else:
        response = jsonify({'message': 'Plan created successfully!'})
        response.set_etag(etag)
        return response, 201

@app.route(VERSION + '/plan', methods=['GET'], defaults={'plan_id': None})
@app.route(VERSION + '/plan/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """
    Get a plan
    """
    try:
        app.logger.info("Handling get plan request")
        plan_details = redis_util.get("plan", plan_id)
        etag = generate_etag(json.dumps(plan_details).encode())

        # Check if client's ETag matches with the current ETag
        if request.headers.get('If-None-Match') == etag:
            return Response(status=304)

    except NotFound as e:
        return Response(status=404)
    except Exception as e:
        return {'message': f'Invalid plan id. Failed to get plan {str(e)}'}, 400
    else:
        response = jsonify(plan_details)
        response.set_etag(etag)
        return response

@app.route(VERSION + '/plan/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """
    Delete a plan
    """
    try:
        app.logger.info("Handling delete plan request")
        redis_util.delete("plan",plan_id)
    except NotFound as e:
        return Response(status=404)
    except Exception as e:
        return {'message': f'Invalid plan id. Failed to delete plan {str(e)}'}, 400
    else:
        return Response(status=204)
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
