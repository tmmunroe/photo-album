import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_iam as iam
import aws_cdk.aws_appsync as appsync

from constructs import Construct
from services.lambda_layer import PythonLambdaLayerWrapper
from services.data_service.data_service import PhotoAlbumDataService
from services.index_service.photo_index_service import PhotoIndexService
from services.search_service.photo_search_service import PhotoSearchService


class PhotoAlbumStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_layer_wrapper = PythonLambdaLayerWrapper(self, 'PythonLambdaLayerTier')
        data_tier = PhotoAlbumDataService(self, 'PhotoAlbumDataTier')

        bucket = data_tier.bucket
        open_search = data_tier.open_search
        open_search_index = 'photo-album-v1'

        index_service = PhotoIndexService(self, 'PhotoIndexService', 
            bucket=bucket, open_search_domain=open_search, open_search_index=open_search_index,
            lambda_layer=lambda_layer_wrapper.layer)
        
        search_service = PhotoSearchService(self, 'PhotoSearchService', 
            bucket=bucket, open_search_domain=open_search, open_search_index=open_search_index,
            lambda_layer=lambda_layer_wrapper.layer)


        # set up api role
        api_role = iam.Role(self, 'APIGatewayRole',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
            role_name='APIGatewayPhotoAlbumRole')

        bucket.grant_put(api_role)
        search_service.lambda_search.grant_invoke(api_role)

        # set up api
        api = apigateway.RestApi(self, 'photo-api',
                rest_api_name='Photo Album Service',
                description='This service serves photos to clients',
                deploy=True,
                deploy_options=apigateway.StageOptions(stage_name='testStage'),
                binary_media_types=["image/jpeg", "image/jpg", "image/png"],
                # default_cors_preflight_options=apigateway.CorsOptions(
                #     allow_origins=apigateway.Cors.ALL_ORIGINS,
                #     allow_headers=apigateway.Cors.DEFAULT_HEADERS,
                #     allow_methods=apigateway.Cors.ALL_METHODS,
                #     status_code=200
                #     )
                )
        api.add_api_key('PhotoAlbumAPIKey')
        options_method = api.root.add_cors_preflight(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_headers=apigateway.Cors.DEFAULT_HEADERS,
            allow_methods=apigateway.Cors.ALL_METHODS,
            status_code=200
        )
        
        photoModel = api.add_model(
            'PhotoModel',
            content_type='image/*',
            model_name='PhotoModel',
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title='photoModel',
                type=apigateway.JsonSchemaType.STRING,
                format='binary'
            )
        )
        
        photo_info_model = api.add_model(
            'SearchResponseModel',
            content_type='application/json',
            model_name='SearchResponseModel',
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title='searchResponse',
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    'url': apigateway.JsonSchema(
                        type=apigateway.JsonSchemaType.STRING),
                    'labels': apigateway.JsonSchema(
                        type=apigateway.JsonSchemaType.ARRAY,
                        items=apigateway.JsonSchema(
                            type=apigateway.JsonSchemaType.STRING)
                        ),
                }
            )
        )

        error_model = api.add_model(
            'ErrorResponseModel',
            content_type='application/json',
            model_name='ErrorResponseModel',
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title='errorResponse',
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    'state': apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING),
                    'message': apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING),
                }
            )
        )

        # search integration for lambda search handler
        search_integration = apigateway.LambdaIntegration(
          search_service.lambda_search,
          credentials_role=api_role
        )
        search_resource = api.root.add_resource('search')
        search_resource.add_method('GET', 
            integration=search_integration,
            # api_key_required=True,
            operation_name='searchPhotos',
            request_parameters= {
                'method.request.querystring.q': True,
            },
            method_responses=[
                apigateway.MethodResponse(status_code='200', 
                    response_models={'application/json': photo_info_model}),
                apigateway.MethodResponse(status_code='403', 
                    response_models={'application/json': error_model}),
                apigateway.MethodResponse(status_code='500', 
                    response_models={'application/json': error_model}),
            ]
        )

        # photos integration for s3
        s3_integration_options = apigateway.IntegrationOptions(
            credentials_role=api_role,
            content_handling=apigateway.ContentHandling.CONVERT_TO_BINARY,
            passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
            integration_responses=[
                apigateway.IntegrationResponse(status_code='200'),
                apigateway.IntegrationResponse(status_code='403'),
                apigateway.IntegrationResponse(status_code='500')
            ],
            request_parameters={
                'integration.request.header.x-amz-meta-customLabels':
                    'method.request.header.x-amz-meta-customLabels',
                'integration.request.path.bucket': f"'{bucket.bucket_name}'",
                'integration.request.path.key': 'method.request.header.imageName',
                'integration.request.header.Content-Type': 'method.request.header.Content-Type',
            }
        )
        photos_integration = apigateway.AwsIntegration(
            service='s3',
            path='{bucket}/{key}',
            integration_http_method='PUT',
            options=s3_integration_options
        )
        photo_resource = api.root.add_resource('photos')
        photo_resource.add_method('PUT',
            integration=photos_integration,
            api_key_required=True,
            operation_name='putPhoto',
            request_parameters={
                'method.request.header.x-amz-meta-customLabels': False,
                'method.request.header.imageName': True,
                'method.request.header.Content-Type': False,
            },
            request_models={
                'image/jpeg': photoModel,
                'image/png': photoModel,
                'image/jpg': photoModel,
            },
            method_responses=[
                apigateway.MethodResponse(status_code='200'),
                apigateway.MethodResponse(status_code='403', 
                    response_models={'application/json': error_model}),
                apigateway.MethodResponse(status_code='500', 
                    response_models={'application/json': error_model}),
            ]
        )


        
        # # expose_headers = 'Set-Cookie,Cookie'.split(',')
        # # allow_headers = 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Set-Cookie,Origin'.split(',')
        # # api.root.add_cors_preflight(allow_credentials=True, allow_origins='[*]', 
        # #     allow_headers=allow_headers, expose_headers=expose_headers)
