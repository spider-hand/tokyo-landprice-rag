from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel


def post_message_service(event: APIGatewayProxyEventModel) -> PostMessageResponse:
    try:
        body = PostMessageRequest.model_validate_json(event.body)

        logger.info({"event": "validate_post_message_request", "body": body})

        # TODO: Interact with external services and get actual response

        return PostMessageResponse(response="Message received: " + body.message)
    except Exception as e:
        logger.exception("Failed to post a message")
        raise e
