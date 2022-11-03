import boto3
import datetime
import json
import os
from opensearchpy import OpenSearch
import requests
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from botocore.exceptions import ClientError
from photo_album_models.open_search_index import OpenSearchIndexModel
from photo_album_models.photo_info import PhotoInfoModel
from photo_album_models.search_response import SearchResponseModel

s3 = boto3.client('s3')


def opensearch_aws_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, 
        'us-east-1', 'es', session_token=credentials.token)


def opensearch_query(label):
    return {
        "query": {
            "match": {
                "labels": label
            }
        }
    }


def search_opensearch(query_terms):
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
    dsl_query = opensearch_query(query_terms)
    # response = search.msearch()
    response = search.search(dsl_query)
    
    print(f"OpenSearch response: {response}")
    hits = response['hits']['hits']
    return [ OpenSearchIndexModel.from_dict(hit['_source']) for hit in hits ]


def perform_search(query) -> SearchResponseModel:
    response = SearchResponseModel()

    results = search_opensearch(query)
    for result in results:
        photo_url = f'https://{result.bucket}.s3.amazonaws.com/{result.objectKey}'
        response.add_photo_info(
            PhotoInfoModel(photo_url, result.labels)
        )

    return response


def lambda_handler(event, context):
    print("Event: ", event)

    query = event["queryStringParameters"].get("q")
    if not query:
        return  {
            "statusCode": 403,
            "body": {
                "message": "BadRequest: query string parameter 'q' was not provided"
            }
        }

    search_response = perform_search(query)

    return {
        "statusCode": 200,
        "body": search_response.format_response()
    }
