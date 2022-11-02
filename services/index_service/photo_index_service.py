import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_iam as iam,
                     aws_lambda as lambda_,
                     aws_opensearchservice as opensearch,
                     aws_s3 as s3,
                     aws_s3_notifications as s3n)

class PhotoIndexService(Construct):
    def __init__(self, scope: Construct, id: str, *,
                bucket: s3.Bucket,
                open_search: opensearch.Domain,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)

        # set up indexer lambda
        self.lambda_index = lambda_.Function(self, "PhotoAlbumIndexer",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("services/index_service/lambdas"),
                    handler="index_photos.lambda_handler",
                    environment=dict(
                        BUCKET=bucket.bucket_name,
                        OPENSEARCH_URL=open_search.domain_endpoint),
                    layers=[lambda_layer]
                    )
        
        # add notifications for bucket and lambda function
        bucket.add_object_created_notification(
            dest=s3n.LambdaDestination(self.lambda_index))
        
        # set up indexer permissions
        self.lambda_index.grant_invoke(iam.ServicePrincipal("s3.amazonaws.com"))
        open_search.grant_read_write(self.lambda_index)

        # rekognition is non-storage API
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        statement.add_resources("*")
        self.lambda_index.add_to_role_policy(statement)

