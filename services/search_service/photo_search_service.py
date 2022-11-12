import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_iam as iam,
                     aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_)


class PhotoSearchService(Construct):
    def __init__(self, scope: Construct, id: str, *, 
                bucket: s3.Bucket,
                open_search_domain: opensearch.Domain,
                open_search_index: str,
                lambda_layer: lambda_.LayerVersion,
                **kwargs):
        super().__init__(scope, id)

        # set up Lex
        lex_bot_id = 'UFYUFHDBYO'
        lex_bot_alias = 'HE6YVHY5FC'

        # set up search lambda
        self.lambda_search = lambda_.Function(self, "PhotoAlbumSearcher",
                    runtime=lambda_.Runtime.PYTHON_3_9,
                    code=lambda_.Code.from_asset("services/search_service/lambdas/"),
                    handler="search_photos.lambda_handler",
                    environment=dict(
                        BUCKET=bucket.bucket_name,
                        OPENSEARCH_HOST=open_search_domain.domain_endpoint,
                        OPENSEARCH_INDEX=open_search_index,
                        LEX_BOT_ID=lex_bot_id,
                        LEX_BOT_ALIAS_ID=lex_bot_alias),
                    layers=[lambda_layer],
                    timeout=cdk.Duration.seconds(10)
                    )
        
        # set up permissions for search
        bucket.grant_read_write(self.lambda_search)
        open_search_domain.grant_read_write(self.lambda_search)

        # set up lex policy
        call_lex_policy = iam.PolicyStatement(actions=["lex:RecognizeText"])
        call_lex_policy.add_resources(
                f"arn:aws:lex:us-east-1:756059218166:bot/{lex_bot_id}",
                f"arn:aws:lex:us-east-1:756059218166:bot-alias/{lex_bot_id}/{lex_bot_alias}"
        )
        self.lambda_search.add_to_role_policy(call_lex_policy)

