from flask import Flask, jsonify
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)

@app.route('/health')
def check_health():
    """
    Route to check health of the application
    """
    app.logger.info("Health request handled successfully")
    return jsonify({'message': 'Application is healthy!'}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
