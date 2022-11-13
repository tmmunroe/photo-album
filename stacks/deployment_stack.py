import aws_cdk as cdk
from aws_cdk import (
    pipelines,
    aws_codebuild as codebuild
)
from constructs import Construct

from stacks.backend_stack import PhotoAlbumStack
from stacks.frontend_stack import PhotoAlbumFrontendStack
from stacks.frontend_deployment_stack import PhotoAlbumFrontendDeploymentStack

class PhotoAlbumDeploymentStage(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None, stage_name=None):
        super().__init__(scope, id, env=env, outdir=outdir, stage_name=stage_name)

        # backend stack
        PhotoAlbumStack(self, "PhotoAlbumStack", env=env)
        
        # frontend stack + separate frontend deployment stack/pipeline 
        frontend_stack = PhotoAlbumFrontendStack(self, "PhotoAlbumFrontendStack", env=env)
        PhotoAlbumFrontendDeploymentStack(self, "PhotoAlbumFrontendDeploymentStack", env=env,
            frontend_bucket=frontend_stack.hosting_bucket)


class PhotoAlbumDeploymentStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # repo source
        repo_source = pipelines.CodePipelineSource.connection(
            repo_string="tmmunroe/photo-album",
            branch="main",
            connection_arn="arn:aws:codestar-connections:us-east-1:756059218166:connection/b439316b-e1a6-4cbe-99eb-3090a0187870")

        # cdk pipeline
        pipeline = pipelines.CodePipeline(self, "PhotoAlbumCDKPipeline", 
                    pipeline_name="PhotoAlbumCDKPipeline",
                    use_change_sets=False,
                    code_build_defaults=pipelines.CodeBuildOptions(
                        build_environment=codebuild.BuildEnvironment(
                            build_image=codebuild.LinuxBuildImage.STANDARD_5_0
                        )
                    ),
                    synth=pipelines.ShellStep("Synth", 
                        input=repo_source,
                        commands=[
                            # install basic environment components
                            "npm install -g aws-cdk",
                            "python --version",
                            "pip install -r requirements.txt",

                            # set up lambda layer
                            "pip install --upgrade -t layer/python -r requirements-lambda.txt",
                            "cp -r photo_album_models layer/python",

                            # synth
                            "cdk synth"
                        ]
                    )
                )
        
        env = cdk.Environment(account='756059218166', region='us-east-1')
        pipeline.add_stage(PhotoAlbumDeploymentStage(self, "DeploymentStage", env=env))