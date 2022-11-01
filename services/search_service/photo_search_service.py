import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_)


class PhotoSearchService(Construct):
    def __init__(self, scope: Construct, id: str, *, 
                photo_bucket: s3.Bucket,
                open_search: opensearch.Domain,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)


        # set up search lambda
        self.lambda_search = lambda_.Function(self, "PhotoAlbumSearcher",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("lambda"),
                    handler="search_photos.lambda_handler",
                    environment=dict(
                        BUCKET=photo_bucket.bucket_name,
                        OPENSEARCH_URL=open_search.domain_endpoint),
                    layers=[lambda_layer]
                    )
        
        # set up permissions for search
        photo_bucket.grant_read_write(self.lambda_search)
        open_search.grant_index_read(self.lambda_search)

        # set up Lex
