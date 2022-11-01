import aws_cdk as cdk
import aws_cdk.aws_s3 as s3

from constructs import Construct
from ..services.data_service import (
    data_service,
    index_service,
    search_service,
    lambda_layer
)

class PhotoAlbumStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        data_tier = data_service.PhotoAlbumDataService(self, "PhotoAlbumDataTier")

        # api = apigateway.RestApi(self, "photo-api",
        #         rest_api_name="Photo Album Service",
        #         description="This service serves photos.")
                
        # api_definition = apigateway.ApiDefinition.fromAsset('resources/photo_api.yml')
        # api = apigateway.SpecRestApi(self, "photo-api", apiDefinition=api_definition)

        # get_photos_integration = apigateway.LambdaIntegration(searcher,
        #         request_templates={"application/json": '{ "statusCode": "200" }'})
        
        # expose_headers = "Set-Cookie,Cookie".split(",")
        # allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Set-Cookie,Origin".split(",")
        # api.root.add_cors_preflight(allow_credentials=True, allow_origins="[*]", 
        #     allow_headers=allow_headers, expose_headers=expose_headers)

        # api = apigateway.RestApi(self, "photo-api",
        #         rest_api_name="Photo Album Service",
        #         description="This service serves photos.")
                
        # # api_definition = apigateway.ApiDefinition.fromAsset('resources/photo_api.yml')
        # # api = apigateway.SpecRestApi(self, "photo-api", apiDefinition=api_definition)

        # get_photos_integration = apigateway.LambdaIntegration(searcher,
        #         request_templates={"application/json": '{ "statusCode": "200" }'})
        
        # # expose_headers = "Set-Cookie,Cookie".split(",")
        # # allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Set-Cookie,Origin".split(",")
        # # api.root.add_cors_preflight(allow_credentials=True, allow_origins="[*]", 
        # #     allow_headers=allow_headers, expose_headers=expose_headers)

        # #index method
        # api.root.add_method("GET", get_photos_integration)   # GET /
        
        # #resource methods
        # photo = api.root.add_resource("{id}")

        # photo_integration = apigateway.LambdaIntegration(indexer)

        # photo.add_method("POST", photo_integration);   # POST /{id}
        # photo.add_method("GET", photo_integration);    # GET /{id}
        # photo.add_method("DELETE", photo_integration); # DELETE /{id}
        