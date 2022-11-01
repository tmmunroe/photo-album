#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.backend_stack import PhotoAlbumStack
from services.data_service.data_service import PhotoAlbumDataStack
from frontend.frontend_stack import PhotoAlbumFrontendStack


env = cdk.Environment(account='756059218166', region='us-east-1')

app = cdk.App()
data_stack = PhotoAlbumDataStack(app, 
    "PhotoAlbumDataStack",
    env=env)

app_stack = PhotoAlbumStack(app, 
    "PhotoAlbumStack",
    env=env,
    bucket=data_stack.bucket,
    open_search=data_stack.open_search)

PhotoAlbumFrontendStack(app,
    "PhotoAlbumFrontend",
    env=env)

app.synth()
