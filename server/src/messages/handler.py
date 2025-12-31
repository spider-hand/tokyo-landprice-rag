from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.logger import dynamic_inject_lambda_context, logger
from messages.service import post_message_service


@dynamic_inject_lambda_context
@event_parser(model=APIGatewayProxyEventModel)
def lambda_handler(event: APIGatewayProxyEventModel, context: LambdaContext):
    logger.info({"event": "post_message"})

    response = post_message_service(event)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": response.model_dump_json(),
    }
