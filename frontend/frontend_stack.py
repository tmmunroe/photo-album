import aws_cdk as cdk
import aws_cdk.aws_s3 as s3

from constructs import Construct
from . import frontend

class PhotoAlbumFrontendStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = s3.Bucket(self, "PhotoAlbumFrontend",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            website_index_document='index.html',
            website_error_document='index.html',
            block_public_access=False,
            public_read_access=True,
        )