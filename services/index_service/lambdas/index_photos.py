import datetime
import json
import urllib.parse
import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

min_confidence = 0.6
max_labels = 10


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
    
    return [ label['Name'] for label in response['Labels'].items() ]


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

    