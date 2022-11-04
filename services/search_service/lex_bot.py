import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_s3 as s3,
                     aws_opensearchservice as opensearch,
                     aws_lambda as lambda_,
                     aws_lex as lex)


def genUtterances(utterances):
    return [lex.CfnBot.SampleUtteranceProperty(utterance=text) for text in utterances]


def genSlot(name, slot_type, has_multiple_values):
    return lex.CfnBot.SlotProperty(name=name, slot_type_name=slot_type, 
        multiple_values_setting=lex.CfnBot.MultipleValuesSettingProperty(allow_multiple_values=has_multiple_values),
        value_elicitation_setting=lex.CfnBot.SlotValueElicitationSettingProperty(slot_constraint="Required")
    )

def genPlainTextMessage(message):
    return lex.CfnBot.ResponseSpecificationProperty(
        message_groups_list=[lex.CfnBot.MessageGroupProperty(
            message=lex.CfnBot.MessageProperty(
                plain_text_message=lex.CfnBot.PlainTextMessageProperty(
                    value=message
                )
            ),
        )],
    )

class PhotoSearchServiceLexBot(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id)
        #create bot
        self.cfn_bot = lex.CfnBot(self, 
            "PhotoSearchServiceLexBot",
            description="Lex Bot for Photo Search Service Query Disambiguation",
            data_privacy={
                "ChildDirected": False,
            },
            idle_session_ttl_in_seconds=60,
            name="PhotoSearchServiceLexTemplate",
            role_arn="roleArn",

            bot_locales=[
                lex.CfnBot.BotLocaleProperty(
                    locale_id="en_US",
                    description="Photo Album Search Service Locale",
                    voice_settings=lex.CfnBot.VoiceSettingsProperty(voice_id="Ivy"),
                    nlu_confidence_threshold=0.4,
                    intents=[
                        lex.CfnBot.IntentProperty(
                            name="SearchIntent",
                            description="Receive a search query request",
                            sample_utterances=genUtterances([
                                "Show me {SearchQuery}",
                                "Let's see {SearchQuery}",
                                "Images of {SearchQuery}",
                                "Pictures of {SearchQuery}",
                                "I want to see {SearchQuery}",
                                "{SearchQuery}"
                            ]),
                            slots=[genSlot("SearchQuery", "AMAZON.SearchQuery", True)],
                            intent_closing_setting=lex.CfnBot.IntentClosingSettingProperty(
                                is_active=True,
                                closing_response=genPlainTextMessage("{SearchQuery}"),
                            ),

                        )
                    ]
                )
            ]
        )


        #create bot version
        self.cfn_bot_version = lex.CfnBotVersion(self, "PhotoSearchServiceLexBotVersion",
            bot_id=self.cfn_bot.attr_id,
            bot_version_locale_specification=[
                lex.CfnBotVersion.BotVersionLocaleSpecificationProperty(
                    locale_id="en_US",
                    bot_version_locale_details=lex.CfnBotVersion.BotVersionLocaleDetailsProperty(
                        source_bot_version="DRAFT"),
                )
            ],
        )

        self.cfn_bot_version.add_depends_on(self.cfn_bot)



        #create bot alias
        self.cfn_bot_alias = lex.CfnBotAlias(self, "PhotoSearchServiceLexBotAlias",
            bot_alias_name="PhotoSearchServiceLexBotAlias1",
            bot_id=self.cfn_bot.attr_id,
            bot_version=self.cfn_bot_version.attr_bot_version
        )

        self.cfn_bot_alias.add_depends_on(self.cfn_bot_version)