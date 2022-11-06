import boto3
import datetime
import json
import os
import requests
import uuid

from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from photo_album_models.open_search_index import OpenSearchIndexModel
from photo_album_models.photo_info import PhotoInfoModel
from photo_album_models.search_response import SearchResponseModel
from requests_aws4auth import AWS4Auth

s3 = boto3.client('s3')
lex = boto3.client('lexv2-runtime')


def opensearch_aws_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, 
        'us-east-1', 'es', session_token=credentials.token)


def opensearch_query(label):
    return {
        "query": {
            "match": {
                "labels": {
                    "query": label,
                    "analyzer": "english"
                }
            }
        }
    }


def search_opensearch(search_terms):
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

    dsl_queries = []
    for term in search_terms:
        dsl_queries.append({})
        dsl_queries.append(opensearch_query(term))

    response = search.msearch(dsl_queries)
    
    print(f"OpenSearch response: {response}")
    hits = []
    for term, term_response in zip(term, response['responses']):
        term_hits = term_response['hits']['hits']
        hits.extend(term_hits)
        print(f"{term}: found {len(term_hits)}")

    return [ OpenSearchIndexModel.from_dict(hit['_source']) for hit in hits ]


def labels_from_text(query):
    bot_id = os.getenv("LEX_BOT_ID")
    alias_id = os.getenv("LEX_BOT_ALIAS_ID")
    
    response = lex.recognize_text(
            botId=bot_id,
            botAliasId=alias_id,
            localeId='en_US',
            sessionId=str(uuid.uuid4()),
            text=query)
    
    print(f"Lex Response: ", response)

    values = response["sessionState"]["intent"]["slots"]["SearchQuery"]["values"]
    labels = [ value["value"]["interpretedValue"] for value in values ]

    return labels


def perform_search(query) -> SearchResponseModel:
    response = SearchResponseModel()

    # disambiguate query
    labels = labels_from_text(query)
    print(f"Labels: {labels}")

    # search opensearch
    results = search_opensearch(labels)
    print(f"Results: {results}")
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
