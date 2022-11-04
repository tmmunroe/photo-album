import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_iam as iam,
                     aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_)
from .lex_bot import PhotoSearchServiceLexBot


class PhotoSearchService(Construct):
    def __init__(self, scope: Construct, id: str, *, 
                bucket: s3.Bucket,
                open_search_domain: opensearch.Domain,
                open_search_index: str,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)

        # set up Lex
        lex_wrapper = PhotoSearchServiceLexBot(self, "PhotoSearchServiceLex")

        # set up search lambda
        self.lambda_search = lambda_.Function(self, "PhotoAlbumSearcher",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("services/search_service/lambdas/"),
                    handler="search_photos.lambda_handler",
                    environment=dict(
                        BUCKET=bucket.bucket_name,
                        OPENSEARCH_HOST=open_search_domain.domain_endpoint,
                        OPENSEARCH_INDEX=open_search_index,
                        LEX_BOT_ID=lex_wrapper.cfn_bot.attr_id,
                        LEX_BOT_ALIAS_ID=lex_wrapper.cfn_bot_alias.attr_bot_alias_id),
                    layers=[lambda_layer]
                    )
        
        # set up permissions for search
        bucket.grant_read_write(self.lambda_search)
        open_search_domain.grant_read_write(self.lambda_search)

        # set up lex policy
        call_lex_policy = iam.PolicyStatement(actions="lex:RecognizeText")
        call_lex_policy.add_resources(
            lex_wrapper.cfn_bot.attr_arn,
            lex_wrapper.cfn_bot_alias.attr_arn
        )
        self.lambda_search.add_to_role_policy(call_lex_policy)

