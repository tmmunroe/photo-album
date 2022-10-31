import boto3
import json
import os
import requests
from botocore.exceptions import ClientError

# s3_client = boto3.resource('s3')
bucket_name = os.getenv('BUCKET')

def lambda_handler(event, context):
    print(f'Event: {event}')
    print(f'Context: {context}')
    print(f'Handling bucket {bucket_name}')
    return {
        "statusCode": 200,
        "body": "Hello world!"
    }