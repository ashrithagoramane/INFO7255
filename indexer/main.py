import json
import os
import time

import pika
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "webapp")

# Elasticsearch configuration
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", 'localhost')
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", 'webapp_index')
ELASTIC_USER = os.getenv("ELASTIC_USER", 'elastic')
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", 'webapp_index')

mappings = json.load(open("./mappings.json"))

es = Elasticsearch([{
        'host': ELASTICSEARCH_HOST, 
        'port': 9200, 
        'scheme': 'https'}], 
        basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
        verify_certs=False)

def create_elasticsearch_index():
    if not es.indices.exists(index=ELASTICSEARCH_INDEX):
        es.indices.create(index=ELASTICSEARCH_INDEX, mappings=mappings)

def index_to_elasticsearch(data):
    try:
        json_data = json.loads(data)
        routing = json_data.get("plan_join", dict()).get("parent")
        es.index(index=ELASTICSEARCH_INDEX, routing=routing, body=json_data, id=json_data.get("objectId"))
        print(f"Indexed data: {json_data}")
    except Exception as e:
        print(f"Error indexing data: {e}")

def callback(ch, method, properties, body):
    # Body will contain the JSON data
    data = body.decode('utf-8')
    index_to_elasticsearch(data)
    print(f"Indexed data: {data}")

def consume_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    create_elasticsearch_index()
    while True:
        consume_from_queue()
        time.sleep(1)  # Adjust the sleep duration as needed
