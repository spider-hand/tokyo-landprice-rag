from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.qdrant import client, COLLECTION_NAME, build_filter
from core.openai import embed, extract_intent, generate_with_llm


def post_message_service(event: APIGatewayProxyEventModel) -> PostMessageResponse:
    try:
        body = PostMessageRequest.model_validate_json(event.body)
        message = body.message

        logger.info({"event": "validate_post_message_request", "body": body})

        # Extract intent from the message
        intent = extract_intent(message)
        logger.info({"event": "extract_intent", "intent": intent})

        # Retrieve relevant information
        hits = client.query_points(
            collection_name=COLLECTION_NAME,
            query=embed(message),
            query_filter=build_filter(intent),
            limit=5,
        ).points

        if not hits:
            return PostMessageResponse(response="関連する情報が見つかりませんでした。")

        # Build contexts
        contexts = []

        for hit in hits:
            logger.info(
                {
                    "event": "retrieved_relevant_information",
                    "score": hit.score,
                    "payload": hit.payload,
                }
            )
            contexts.append(hit.payload["semantic_text"])

        # Generate answer
        response = generate_with_llm(question=message, contexts=contexts)
        logger.info({"event": "generate_with_llm", "response": response})
        return PostMessageResponse(response=response)
    except Exception as e:
        logger.exception("Failed to post a message")
        raise e
