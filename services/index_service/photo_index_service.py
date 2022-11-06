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
                open_search_domain: opensearch.Domain,
                open_search_index: str,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)

        #set up lambda to create index
        create_index_lambda = lambda_.Function(self, "PhotoAlbumCreateIndex",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("services/index_service/lambdas-mgmt"),
                    handler="generate_photos_index.lambda_handler",
                    environment=dict(
                        OPENSEARCH_HOST=open_search_domain.domain_endpoint,
                        OPENSEARCH_INDEX=open_search_index),
                    layers=[lambda_layer],
                    timeout=cdk.Duration.seconds(10)
                    )

        # set up indexer lambda
        self.lambda_index = lambda_.Function(self, "PhotoAlbumIndexer",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("services/index_service/lambdas"),
                    handler="index_photos.lambda_handler",
                    environment=dict(
                        BUCKET=bucket.bucket_name,
                        OPENSEARCH_HOST=open_search_domain.domain_endpoint,
                        OPENSEARCH_INDEX=open_search_index),
                    layers=[lambda_layer],
                    timeout=cdk.Duration.seconds(10)
                    )
        
        # add notifications for bucket and lambda function
        bucket.add_object_created_notification(
            dest=s3n.LambdaDestination(self.lambda_index))
        
        # set up indexer permissions
        self.lambda_index.grant_invoke(iam.ServicePrincipal("s3.amazonaws.com"))
        bucket.grant_read(self.lambda_index)
        open_search_domain.grant_read_write(self.lambda_index)
        open_search_domain.grant_read_write(create_index_lambda)
        bucket.grant_read(iam.ServicePrincipal("rekognition.amazonaws.com"))

        # rekognition is non-storage API
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        statement.add_resources("*")
        self.lambda_index.add_to_role_policy(statement)

