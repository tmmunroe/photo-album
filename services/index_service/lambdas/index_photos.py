import boto3
import json
import os
import requests
from botocore.exceptions import ClientError

# s3_client = boto3.resource('s3')
bucket_name = os.getenv('BUCKET')


def get_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello world from GET HANDLER!"
    }


def put_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello world from PUT HANDLER!"
    }


def post_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello world from POST HANDLER!"
    }


def lambda_handler(event, context):
    method = event.get('httpMethod')
    print(f'Event: {event}')
    print(f'Context: {context}')
    print(f'Handling bucket {bucket_name}')

    if method == 'GET':
        return get_handler(event, context)
    elif method == 'PUT':
        return put_handler(event, context)
    elif method == 'POST':
        return post_handler(event, context)
    else:
        return {
            "statusCode": 503,
            "body": f"Server failure: failed to find method {method}"
        }
