import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_lambda as lambda_,
                     RemovalPolicy)


class PhotoService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        bucket = s3.Bucket(self, "PhotoAlbum",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        layer = lambda_.LayerVersion(self, 'python_layer',
                                     code=lambda_.Code.from_asset("layer"),
                                     description='Common helper utility',
                                     compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
                                     removal_policy=RemovalPolicy.DESTROY)

        handler = lambda_.Function(self, "PhotoAlbumHandler",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("lambda"),
                    handler="photos.lambda_handler",
                    environment=dict(BUCKET=bucket.bucket_name),
                    layers=[layer]
                    )

        bucket.grant_read_write(handler)

        api = apigateway.RestApi(self, "photo-api",
                rest_api_name="Photo Album Service",
                description="This service serves photos.")
                
        # api_definition = apigateway.ApiDefinition.fromAsset('resources/photo_api.yml')
        # api = apigateway.SpecRestApi(self, "photo-api", apiDefinition=api_definition)

        get_photos_integration = apigateway.LambdaIntegration(handler,
                request_templates={"application/json": '{ "statusCode": "200" }'})
        
        # expose_headers = "Set-Cookie,Cookie".split(",")
        # allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Set-Cookie,Origin".split(",")
        # api.root.add_cors_preflight(allow_credentials=True, allow_origins="[*]", 
        #     allow_headers=allow_headers, expose_headers=expose_headers)

        api.root.add_method("GET", get_photos_integration)   # GET /