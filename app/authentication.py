from flask import request, jsonify
from functools import wraps
from google.auth.transport import requests
from google.oauth2 import id_token
import os
from dotenv import load_dotenv

load_dotenv()


CLIENT_ID = os.getenv("GCP_CLIENT_ID")


def validate_id_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return id_info
    except Exception as e:
        print("ID Token validation failed:", e)
        return None


# def validate_access_token(token):
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"]
#     )

#     try:
#         token_info = credentials.token_info(requests.Request(), token)
#         return token_info
#     except Exception as e:
#         print("Access Token validation failed:", e)
#         return None


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            token_parts = auth_header.split(" ")
            if len(token_parts) == 2 and token_parts[0] == "Bearer":
                token = token_parts[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        id_info = validate_id_token(token)
        if id_info:
            kwargs["token_info"] = id_info
            return f(*args, **kwargs)

        # access_token_info = validate_access_token(token)
        # if access_token_info:
        #     kwargs["token_info"] = access_token_info
        #     return f(*args, **kwargs)

        return jsonify({"message": "Token is invalid"}), 401

    return decorated_function
