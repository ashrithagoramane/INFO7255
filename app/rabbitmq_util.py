import os

import pika
from dotenv import load_dotenv
import json
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "webapp")


def push_to_queue(data):
    json_str = json.dumps(data)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_publish(exchange="", routing_key=RABBITMQ_QUEUE, body=json_str)
    connection.close()
