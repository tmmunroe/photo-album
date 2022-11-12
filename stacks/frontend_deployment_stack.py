import aws_cdk as cdk
import aws_cdk as cdk
from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
)
from constructs import Construct


class PhotoAlbumFrontendDeploymentStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, frontend_bucket=None, env=None) -> None:
        super().__init__(scope, construct_id, env=env)
        
        # set up artifacts
        source_artifact = codepipeline.Artifact("SourceArtifact")
        build_artifact = codepipeline.Artifact("BuildArtifact")
        
        # pipeline
        pipeline = codepipeline.Pipeline(self, "PhotoAlbumFrontendDeployment")

        # add source
        pipeline.add_stage(
            stage_name="Source",
            actions=[
                actions.CodeStarConnectionsSourceAction(
                    action_name="SourcePhotoAlbumFrontend",
                    connection_arn='arn:aws:codestar-connections:us-east-1:756059218166:connection/b439316b-e1a6-4cbe-99eb-3090a0187870',
                    owner='tmmunroe',
                    repo='photo-album-frontend',
                    branch='main',
                    output=source_artifact,
                )
            ]
        )

        # add build - note that build spec is in the frontend repo
        pipeline.add_stage(
            stage_name="Build",
            actions=[
                actions.CodeBuildAction(
                    action_name="BuildPhotoAlbumFrontend",
                    input=source_artifact,
                    outputs=[build_artifact],
                    project=codebuild.PipelineProject(
                        self, "PhotoAlbumFrontendProject",
                        environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_6_0 # Ubuntu 22
                        ),
                        build_spec=codebuild.BuildSpec.from_source_filename('buildspec.yml')
                    )
                ),
            ]
        )

        # add deploy
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                actions.S3DeployAction(
                    action_name='Deploy',
                    bucket=frontend_bucket,
                    input=build_artifact,
                    extract=True,
                    access_control=s3.BucketAccessControl.PUBLIC_READ,
                    run_order=1
                )
            ]
        )