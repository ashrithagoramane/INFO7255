import json
import logging

import backend
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_expects_json import expects_json
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.http import generate_etag

load_dotenv()

VERSION = "/v1"

logging.basicConfig(filename="app.log", level=logging.DEBUG)
schema = json.load(open("./schemas/plan_schema.json"))
app = Flask(__name__)


@app.route(VERSION + "/health", methods=["GET"])
def check_health():
    """
    Route to check health of the application
    """
    app.logger.info("Health request handled successfully")
    return jsonify({"message": "Application is healthy!"}), 200


@app.route(VERSION + "/plan", methods=["POST"])
@expects_json(schema=schema)
def create_object():
    """
    Create a object
    """
    try:
        app.logger.info("Handling create object request")
        request_data = request.get_json()
        response_data = backend.insert_object(request_data)
        etag = generate_etag(json.dumps(response_data).encode())
    except BadRequest as e:
        return {"message": f"{str(e)}"}, 400
    except Exception as e:
        return {"message": f"Invalid request JSON. Failed to create user {str(e)}"}, 400
    else:
        response = jsonify({"message": "Plan created successfully!"})
        response.set_etag(etag)
        return response, 201


@app.route(VERSION + "/<object_type>", methods=["GET"], defaults={"object_id": None})
@app.route(VERSION + "/<object_type>/<object_id>", methods=["GET"])
def get_object(object_type, object_id):
    """
    Get a object
    """
    try:
        app.logger.info("Handling get object request")
        object_details = backend.get_object(object_type, object_id)

        etag = generate_etag(json.dumps(object_details).encode())

        # Check if client's ETag matches with the current ETag
        if request.headers.get("If-None-Match") == etag:
            return Response(status=304)

    except NotFound as e:
        return Response(status=404)
    except Exception as e:
        return {"message": f"Invalid plan id. Failed to get plan {str(e)}"}, 400
    else:
        response = jsonify(object_details)
        response.set_etag(etag)
        return response

@app.route(VERSION + "/<object_type>/<object_id>", methods=["DELETE"])
def delete_object(object_type, object_id):
    """
    Delete an object
    """
    try:
        app.logger.info("Handling delete plan request")
        backend.delete_object(object_type, object_id)
    except NotFound as e:
        return Response(status=404)
    except Exception as e:
        return {"message": f"Invalid plan id. Failed to delete plan {str(e)}"}, 400
    else:
        return Response(status=204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
