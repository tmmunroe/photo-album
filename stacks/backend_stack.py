import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_iam as iam

from constructs import Construct
from services.lambda_layer import PythonLambdaLayer
from services.data_service.data_service import PhotoAlbumDataService
from services.index_service.photo_index_service import PhotoIndexService
from services.search_service.photo_search_service import PhotoSearchService


class PhotoAlbumStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_layer = PythonLambdaLayer(self, "PythonLambdaLayer")
        data_tier = PhotoAlbumDataService(self, "PhotoAlbumDataTier")

        bucket = data_tier.bucket
        open_search = data_tier.open_search

        index_service = PhotoIndexService(self, "PhotoIndexService", 
            bucket=bucket, open_search=open_search, lambda_layer=lambda_layer)
        
        # search_service = PhotoSearchService(self, "PhotoSearchService", 
        #     bucket=bucket, open_search=open_search, lambda_layer=lambda_layer)

        # # api = apigateway.RestApi(self, "photo-api",
        # #         rest_api_name="Photo Album Service",
        # #         description="This service serves photos to clients")
                
        # api_definition = apigateway.ApiDefinition.from_asset('api/photo_api.yml')
        # api = apigateway.SpecRestApi(self, "photo-api", api_definition=api_definition)

        # search_service_integration = apigateway.LambdaIntegration(search_service.lambda_search,
        #         request_templates={"application/json": '{ "statusCode": "200" }'})
        
        # post_photo_integration = apigateway.AwsIntegration(
        #     service="s3",
        #     path="{bucket}/{key}",
        #     integration_http_method="POST",
        # )

        # upload = api.root.add_method("POST", post_photo_integration)
        # search = api.root.add_method("GET", search_service_integration)

        # bucket.grant_put(api.root)
        # search_service.lambda_search.grant_invoke(api)

        
        # # expose_headers = "Set-Cookie,Cookie".split(",")
        # # allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Set-Cookie,Origin".split(",")
        # # api.root.add_cors_preflight(allow_credentials=True, allow_origins="[*]", 
        # #     allow_headers=allow_headers, expose_headers=expose_headers)
