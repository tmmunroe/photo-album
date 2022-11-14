import aws_cdk as cdk
import aws_cdk as cdk
from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    aws_codeartifact as codeartifact,
    aws_cloudfront as cloudfront,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct


class PhotoAlbumLambdaDeploymentStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, env=None, search_lambda:lambda_.IFunction=None, index_lambda:lambda_.IFunction=None) -> None:
        super().__init__(scope, construct_id, env=env)
        
        # set up artifacts
        source_artifact = codepipeline.Artifact("LambdaSourceArtifact")
        build_artifact = codepipeline.Artifact("LambdaBuildArtifact")
        
        # pipeline
        pipeline = codepipeline.Pipeline(self, "PhotoAlbumLambdaDeployment")

        # add source
        pipeline.add_stage(
            stage_name="SourceLambdas",
            actions=[
                actions.CodeStarConnectionsSourceAction(
                    action_name="SourcePhotoAlbumL",
                    connection_arn='arn:aws:codestar-connections:us-east-1:756059218166:connection/b439316b-e1a6-4cbe-99eb-3090a0187870',
                    owner='tmmunroe',
                    repo='photo-album',
                    branch='main',
                    output=source_artifact,
                )
            ]
        )

        # add build/deploy - note that build spec is in the repo
        project = codebuild.PipelineProject(
                        self, "PhotoAlbumLambdasProject",
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_6_0 # Ubuntu 22
                        ),
                        build_spec=codebuild.BuildSpec.from_object({
                            "version": "0.2",
                            "phases": {
                                "build": {
                                    "commands": [
                                        "python --version",
                                        "pip install -r requirements.txt",
                                        "zip -j search_code.zip services/search_service/lambdas/search_photos.py",
                                        "zip -j index_code.zip services/index_service/lambdas/index_photos.py",
                                        f"aws lambda update-function-code --function-name \"{search_lambda.function_name}\" --zip-file fileb://search_code.zip",
                                        f"aws lambda update-function-code --function-name \"{index_lambda.function_name}\" --zip-file fileb://index_code.zip",
                                    ]
                                },
                            }
                        })
                    )
        
        # give project permission to update function codes
        project.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["lambda:UpdateFunctionCode"],
            resources=[search_lambda.function_arn, index_lambda.function_arn]
        ))

        pipeline.add_stage(
            stage_name="FilterAndUploadLambdas",
            actions=[
                actions.CodeBuildAction(
                    action_name="BuildPhotoAlbumLambdas",
                    input=source_artifact,
                    outputs=[build_artifact],
                    project=project
                ),
            ]
        )

        # # add deploy
        # pipeline.add_stage(
        #     stage_name="Deploy",
        #     actions=[
        #         actions.Action(
        #             "SearchLambdaQuickDeploy",
        #             artifact_bounds=codepipeline.ActionArtifactBounds(1, 1, 1, 1),
        #             category=codepipeline.ActionCategory.DEPLOY,
        #         )
        #         # actions.S3DeployAction(
        #         #     action_name='Deploy',
        #         #     bucket=frontend_bucket,
        #         #     input=build_artifact,
        #         #     extract=True,
        #         #     access_control=s3.BucketAccessControl.PUBLIC_READ,
        #         #     run_order=1
        #         # )
        #     ]
        # )