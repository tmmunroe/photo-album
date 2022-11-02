
import boto3
import datetime
import json
import os
import requests
from requests_aws4auth import AWS4Auth
import urllib.parse


s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

min_confidence = 0.6
max_labels = 10

opensearch_index = 'photo-album'

def requests_aws_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, 
        credentials.secret_key,
        region='us-east-1',
        service='es',
        session_token=credentials.token)


def post_to_opensearch(labeled_bucket_info):
    url = os.getenv['OPENSEARCH_URL']
    index_endpoint = f'{url}/photo-album/_doc'
    awsauth = requests_aws_auth()
    
    response = requests.post(
        url=index_endpoint,
        auth=awsauth,
        data=labeled_bucket_info,
        headers={'Content-Type': 'application/json'}
    )

    print(f"OpenSearch response: {response}")

        

def get_labels(bucket, key):
    try:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                    }
                },
            MaxLabels=max_labels,
            MinConfidence=min_confidence
        )
    except Exception as e:
        print(e)
        print(f"Error getting {key} from bucket {bucket}")
        raise e
    
    print(response['Labels'])
    return [ label['Name'] for label in response['Labels'] ]


def lambda_handler(event, context):
    print("Event: " + json.dumps(event))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(f"Bucket: {bucket}")
    print(f"Key: {key}")

    labels = get_labels(bucket, key)
    print(labels)

    labeled_bucket_info = {
        "bucket": bucket,
        "objectKey": key,
        "createdTimestamp": datetime.datetime.now().timestamp(),
        "labels": labels
    }
    print(labeled_bucket_info)

    