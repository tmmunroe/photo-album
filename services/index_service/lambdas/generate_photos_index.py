
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


def lambda_handler(event, context):
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

    response = search.indices.create(index=index, body=create_params)
    print(f"OpenSearch response: {response}")

    return response
