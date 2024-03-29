import base64
import boto3
import datetime
import json
import os
import requests
import uuid

from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from photo_album_models.open_search_index import OpenSearchIndexModel
from photo_album_models.photo import PhotoModel
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

    response = search.msearch(dsl_queries, index=index)
    
    print(f"OpenSearch response: {response}")
    results = {} # by bucket,objectKey - this helps to prevent returning the same image more than once
    for term, term_response in zip(term, response['responses']):
        term_hits = term_response['hits']['hits']
        for hit in term_hits:
            index_model = OpenSearchIndexModel.from_dict(hit['_source'])
            results[(index_model.bucket, index_model.objectKey)] = index_model

        print(f"{term}: found {len(term_hits)}")

    return list(results.values())


def labels_from_text(query):
    labels = []

    bot_id = os.getenv("LEX_BOT_ID")
    alias_id = os.getenv("LEX_BOT_ALIAS_ID")
    
    response = lex.recognize_text(
            botId=bot_id,
            botAliasId=alias_id,
            localeId='en_US',
            sessionId=str(uuid.uuid4()),
            text=query)
    
    print(f"Lex Response: ", response)

    first = response["sessionState"]["intent"]["slots"]["SearchQuery1"]
    second = response["sessionState"]["intent"]["slots"]["SearchQuery2"]

    labels.append(first['value']['interpretedValue']) # first has to be there
    if second:
        labels.append(second['value']['interpretedValue'])

    return labels


def perform_search(query) -> SearchResponseModel:
    response = SearchResponseModel()

    # disambiguate query
    labels = labels_from_text(query)
    print(f"Labels: {labels}")
    if len(labels) == 0:
        return response

    # search opensearch
    results = search_opensearch(labels)
    print(f"Results: {results}")
    for result in results:
        s3_response = s3.get_object(Bucket=result.bucket, Key=result.objectKey)
        print(s3_response)
        streaming_body, content_type = s3_response['Body'], s3_response['ContentType']
        body = base64.encodebytes(streaming_body.read()).decode('utf-8')
        print(f'Body: {body}')
        print(f'ContentType: {content_type}')

        response.add_photo(PhotoModel(body))

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
    # test change
    print("Search response: ", search_response)

    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Origin",
        },
        "body": json.dumps(search_response.format_response())
    }
    print('Response: ', response)

    return response
