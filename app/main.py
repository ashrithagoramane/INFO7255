from flask import Flask, jsonify, request
from werkzeug.http import generate_etag
from dotenv import load_dotenv
import logging
from flask_expects_json import expects_json
import redis_util
import json

load_dotenv()

logging.basicConfig(filename='app.log', level=logging.DEBUG)

schema = json.load(open('./schemas/plan_schema.json'))

app = Flask(__name__)

@app.route('/health', methods=["GET"])
def check_health():
    """
    Route to check health of the application
    """
    app.logger.info("Health request handled successfully")
    return jsonify({'message': 'Application is healthy!'}), 200

@app.route('/plan', methods=['POST'])
@expects_json(schema=schema)
def create_plan():
    """
    Create a plan
    """
    try:
        request_data = request.get_json()
        response_data = redis_util.create_plan(request_data)
        etag = generate_etag(json.dumps(response_data).encode())
        app.logger.info("Handling create plan request")
    except Exception as e:
        return {'message': 'Invalid request JSON. Failed to create user'}, 400
    else:
        response = jsonify({'message': 'Plan created successfully!'})
        response.set_etag(etag)
        return response, 201

@app.route('/plan', methods=['GET'], defaults={'plan_id': None})
@app.route('/plan/<plan_id>', methods=['GET'])
def get_plan_by_id(plan_id):
    """
    Get a plan
    """
    try:
        plan_details = redis_util.get_plan(plan_id)
        etag = generate_etag(json.dumps(plan_details).encode())

        # Check if client's ETag matches with the current ETag
        if request.headers.get('If-None-Match') == etag:
            return '', 304

        app.logger.info("Handling get plan request")
    except Exception as e:
        return {'message': f'Invalid request JSON. Failed to create user {str(e)}'}, 400
    else:
        response = jsonify(plan_details)
        response.set_etag(etag)
        return response, 201

@app.route('/plan/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """
    Delete a plan
    """
    try:
        redis_util.delete_plan(plan_id)
        app.logger.info("Handling delete plan request")
    except Exception as e:
        return {'message': f'Invalid request JSON. Failed to create user {str(e)}'}, 400
    else:
        return {}, 204
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
