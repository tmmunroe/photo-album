import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_,
                     RemovalPolicy)

class PythonLambdaLayer(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # python layer for lambda function dependencies
        self.layer = lambda_.LayerVersion(self, "python_layer",
                                     code=lambda_.Code.from_asset("layer"),
                                     description="Common helper utility",
                                     compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
                                     removal_policy=RemovalPolicy.DESTROY)