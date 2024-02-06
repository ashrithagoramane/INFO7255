from flask import Flask, jsonify
from dotenv import load_dotenv
import logging
from flask_expects_json import expects_json
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
        app.logger.info("Handling create plan request")
    except Exception as e:
        return {'message': 'Invalid request JSON. Failed to create user'}, 400
    else:
        return jsonify({'message': 'Plan created successfully!'}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
