import aws_cdk as cdk
import aws_cdk.aws_s3 as s3

from constructs import Construct

class PhotoAlbumStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "PhotoAlbumQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        bucket = s3.Bucket(self, "PhotoAlbumBucket",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)
