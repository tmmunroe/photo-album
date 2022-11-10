import aws_cdk as cdk
from aws_cdk import (
    pipelines,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as actions
)
from constructs import Construct

from stacks.backend_stack import PhotoAlbumStack
from stacks.frontend_stack import PhotoAlbumFrontendStack


class PhotoAlbumDeploymentStage(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None, stageName=None):
        super().__init__(scope, id, env=env, outdir=outdir, stageName=stageName)

        PhotoAlbumStack(self, "PhotoAlbumStack", env=env)
        PhotoAlbumFrontendStack(self, "PhotoAlbumFrontendStack", env=env)


class PhotoAlbumDeploymentStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # oauth token for access to repos
        secret = cdk.SecretValue.secrets_manager("codepipeline/photo-album")

        source = codepipeline.Artifact("SourceArtifact")
        pipe = codepipeline.Pipeline(self, "PhotoAlbumPipeline")
        pipe.add_stage(
            stage_name="Source",
            actions=[
                actions.GitHubSourceAction(
                    action_name="github-source",
                    oauth_token=secret,
                    output=source,
                    owner="tmmunroe",
                    repo="photo-album",
                    trigger=actions.GitHubTrigger.WEBHOOK
                )
            ]
        )

        pipe.add_stage(
            stage_name="Build",
            actions=[
                actions.CodeBuildAction(
                    input=source,
                    project=codebuild.PipelineProject(
                        self, "PhotoAlbumFrontEndCodeBuild",
                        build_spec=codebuild.BuildSpec(
                            
                        )
                    )
                )
            ]
        )

        # cdk pipeline
        repo_source = pipelines.CodePipelineSource.git_hub(
            repo_string="tmmunroe/photo-album",
            branch="main", 
            authentication=secret,
            trigger=actions.GitHubTrigger.WEBHOOK)


        pipeline = pipelines.CodePipeline(self, "PhotoAlbumCDKPipeline", 
                    pipeline_name="PhotoAlbumCDKPipeline",
                    synth=pipelines.ShellStep("Synth", 
                        input=repo_source,
                        commands=[
                            "npm install -g aws-cdk", 
                            "python -m pip install -r requirements.txt",
                            "pip install --upgrade -t layer/python -r requirements-lambda.txt",
                            "cp -r photo_album_models layer/python",
                            "cdk synth"
                        ]
                    )
                )

        
        env = cdk.Environment(account='756059218166', region='us-east-1')
        pipeline.add_stage(PhotoAlbumDeploymentStage(self, "DeploymentStage", env=env))