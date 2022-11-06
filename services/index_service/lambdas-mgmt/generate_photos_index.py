
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


def opensearch_aws_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, 
        'us-east-1', 'es', session_token=credentials.token)


def opensearch_client():
    host = os.getenv('OPENSEARCH_HOST')
    awsauth = opensearch_aws_auth()

    return OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )


def create_index():
    index = os.getenv('OPENSEARCH_INDEX')
    search_client = opensearch_client()
    create_params = {
        "mappings": {
            "properties": {
                "bucket": { "type": "text" },
                "objectKey": { "type": "text" },
                "createdTimestamp": { "type": "float" },
                "labels": {
                    "type": "text",
                    "analyzer": "english"
                }
            }
        }
    }

    return search_client.indices.create(index=index, body=create_params)


def delete_index():
    index = os.getenv('OPENSEARCH_INDEX')
    search_client = opensearch_client()
    return search_client.indices.delete(index)


def reset_index():
    response = delete_index()
    print('Delete Response: ', response)

    response = create_index()
    print('Create Response: ', response)

    return ''


def lambda_handler(event, context):
    operation = event.get('operation')
    if not operation:
        raise ValueError(f'No operation specified')
        return None

    if operation == 'create':
        response = create_index()
    elif operation == 'delete':
        response = delete_index()
    elif operation == 'reset':
        response = reset_index()
    else:
        raise ValueError(f'{operation} not a recognized operation')

    print(f"Response: {response}")
