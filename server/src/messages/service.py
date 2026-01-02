from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.qdrant import client, COLLECTION_NAME
from core.openai import embed


def post_message_service(event: APIGatewayProxyEventModel) -> PostMessageResponse:
    try:
        body = PostMessageRequest.model_validate_json(event.body)

        logger.info({"event": "validate_post_message_request", "body": body})

        vector = embed(body.message)

        hits = client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=5,
        ).points

        if not hits:
            logger.info({"event": "no_relevant_information_found"})
            return PostMessageResponse(response="No relevant information found.")

        for hit in hits:
            logger.info(
                {
                    "event": "retrieved_relevant_information",
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                }
            )

        return PostMessageResponse(response=hits[0].payload.get("text", ""))
    except Exception as e:
        logger.exception("Failed to post a message")
        raise e
