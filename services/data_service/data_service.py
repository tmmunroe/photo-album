import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_opensearchservice as opensearch)


class PhotoAlbumDataService(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(self, "PhotoAlbumS3",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        self.open_search = opensearch.Domain(self, "PhotoAlbumOpenSearch",
            version=opensearch.EngineVersion.OPENSEARCH_1_3,
            capacity=opensearch.CapacityConfig(
                data_node_instance_type='t3.small.search',
                master_node_instance_type='t3.small.search'
            ),
            ebs=opensearch.EbsOptions(
                volume_size=10,
                volume_type=ec2.EbsDeviceVolumeType.GP2
            ),
            node_to_node_encryption=True,
            # security_groups=None,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True
            ))