import aws_cdk as cdk
from aws_cdk import (
     aws_s3 as s3,
     aws_cloudfront as cloudfront,
     aws_cloudfront_origins as origins,
     aws_certificatemanager as acm,
     aws_route53 as route53,
     aws_route53_targets as targets
)

from constructs import Construct

class PhotoAlbumFrontendStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        domain_name = "photo-album-tmm2169.com"

        # s3 bucket for hosting
        self.hosting_bucket = s3.Bucket(self, "PhotoAlbumFrontend",
            bucket_name=domain_name,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            website_index_document='index.html',
            website_error_document='index.html',
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
        )

        # hosted zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "route53-hosted-zone", 
            hosted_zone_id="Z05376351NPXVZBCCCUZ0",
            zone_name=domain_name)

        # certificate
        certificate = acm.Certificate.from_certificate_arn(self, "route53-domain-certificate", "arn:aws:acm:us-east-1:756059218166:certificate/c11593ac-b285-4707-8744-0f97d5173416")

        # cloud front
        distribution = cloudfront.Distribution(self, "PhotoAlbumCloudFront",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.hosting_bucket),
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            domain_names=[domain_name],
            certificate=certificate,
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            error_responses=[ # for SPA apps, need redirects to index
                cloudfront.ErrorResponse(http_status=403, response_http_status=200, response_page_path="/index.html"),
                cloudfront.ErrorResponse(http_status=404, response_http_status=200, response_page_path="/index.html"),
            ]
        )

        # route53 dns record
        route53.ARecord(self, "PhotoAlbumARecord",
            record_name=domain_name,
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution)),
            delete_existing=True)