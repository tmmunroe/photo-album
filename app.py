#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.deployment_stack import PhotoAlbumDeploymentStack

app = cdk.App()
PhotoAlbumDeploymentStack(app, "PhotoAlbumDeploymentStack", 
    env=cdk.Environment(account='756059218166', region='us-east-1'))

app.synth()
