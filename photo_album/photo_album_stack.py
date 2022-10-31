import aws_cdk as cdk
import aws_cdk.aws_s3 as s3

from constructs import Construct
from . import photo_album_service

class PhotoAlbumStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #create photo service
        photo_album_service.PhotoService(self, "PhotoAlbum")