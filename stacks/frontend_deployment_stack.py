# import aws_cdk as cdk
# import aws_cdk as cdk
# from aws_cdk import (
#     aws_codebuild as codebuild,
#     aws_codepipeline as codepipeline,
#     aws_codepipeline_actions as actions
# )
# from constructs import Construct


# class PhotoAlbumFrontendDeploymentStack(cdk.Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)
        
#         bucket = s3.Bucket(self, "PhotoAlbumFrontendDeploymentStack",
#             versioned=True,
#             removal_policy=cdk.RemovalPolicy.DESTROY,
#             auto_delete_objects=True,
#             website_index_document='index.html',
#             website_error_document='index.html',
#             public_read_access=True,
#             block_public_access=s3.BlockPublicAccess(
#                 block_public_acls=False,
#                 block_public_policy=False,
#                 ignore_public_acls=False,
#                 restrict_public_buckets=False
#             )
#         )
