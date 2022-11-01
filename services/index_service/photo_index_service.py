import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_,
                     aws_rekognition as rekognition,
                     RemovalPolicy)


class PhotoIndexService(Construct):
    def __init__(self, scope: Construct, id: str, *,
                photo_bucket: s3.Bucket,
                open_search: opensearch.Domain,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)

        # set up indexer lambda
        self.lambda_index = lambda_.Function(self, "PhotoAlbumIndexer",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("lambdas"),
                    handler="index_photos.lambda_handler",
                    environment=dict(
                        BUCKET=photo_bucket.bucket_name,
                        OPENSEARCH_URL=open_search.domain_endpoint),
                    layers=[layer]
                    )

        # set up indexer permissions
        self.lambda_index.grant_invoke(photo_bucket)
        open_search.grant_index_read_write(self.lambda_index)

        # rekognition is non-storage API
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        statement.add_resources("*")
        self.lambda_index.add_to_role_policy(statement)

