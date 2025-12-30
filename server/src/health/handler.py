import json
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.logger import dynamic_inject_lambda_context, logger
from core.secret import get_secret


@dynamic_inject_lambda_context
def lambda_handler(event: APIGatewayProxyEventModel, context: LambdaContext) -> dict:
    secrets = get_secret()
    test_secret = secrets.get("test")
    logger.info({"event": "health_check", "test_secret": test_secret})
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "pong"}),
    }
