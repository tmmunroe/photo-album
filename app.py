#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.backend_stack import PhotoAlbumStack
from frontend.frontend_stack import PhotoAlbumFrontendStack


env = cdk.Environment(account='756059218166', region='us-east-1')

app = cdk.App()

PhotoAlbumStack(app, "PhotoAlbumStack", env=env)
# PhotoAlbumFrontendStack(app, "PhotoAlbumFrontend", env=env)

app.synth()
