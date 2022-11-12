
import boto3
import datetime
import json
import os
from opensearchpy import OpenSearch
import requests
from requests_aws4auth import AWS4Auth
import urllib.parse
from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

min_confidence = 0.6
max_labels = 10


def opensearch_aws_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, 
        'us-east-1', 'es', session_token=credentials.token)


def post_to_opensearch(labeled_bucket_info):
    host = os.getenv('OPENSEARCH_HOST')
    index = os.getenv('OPENSEARCH_INDEX')
    awsauth = opensearch_aws_auth()

    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    response = search.index(index=index, body=labeled_bucket_info)
    
    print(f"OpenSearch response: {response}")
    return response


def get_labels(bucket, key):
    labels = []
    try:
        # get rekognition labels
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
        print(f'Rekognition: {response}')
        rekognition_labels = [label['Name'] for label in response['Labels']]
        print(f'Rekognition Labels: {rekognition_labels}')

        # get s3 custom labels
        response = s3.head_object(Bucket=bucket, Key=key)
        print(f'S3: {response}')
        custom_labels = response['Metadata'].get('customlabels', list())
        if isinstance(custom_labels, str):
            custom_labels = [custom_labels]
        print(f'Custom Labels: {custom_labels}')
        
        labels.extend(rekognition_labels + custom_labels)
    except Exception as e:
        print(e)
        raise e
    
    print(labels)
    return labels


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

    post_to_opensearch(labeled_bucket_info)

    