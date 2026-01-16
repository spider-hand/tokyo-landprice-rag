from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.qdrant import build_filter, build_geo_filter, retrieve_contexts
from core.openai import embed, extract_intent, generate_with_llm


def post_message_service(event: APIGatewayProxyEventModel) -> PostMessageResponse:
    try:
        body = PostMessageRequest.model_validate_json(event.body)
        message = body.message
        lat = body.lat
        lon = body.lon
        is_point = body.is_point
        language = body.language

        logger.info({"event": "validate_post_message_request", "body": body})

        query_filter = None

        if lat is not None and lon is not None:
            bbox_size = 100 if is_point else 500
            query_filter = build_geo_filter(lat, lon, bbox_size)
            logger.info(
                {
                    "event": "build_geo_filter",
                    "lat": lat,
                    "lon": lon,
                    "bbox_size": bbox_size,
                }
            )
        else:
            intent = extract_intent(message)
            logger.info(
                {
                    "event": "extract_intent",
                    "intent": intent,
                }
            )
            query_filter = build_filter(intent)

        vector = embed(message)
        result = retrieve_contexts(vector, query_filter)

        if not result.hits:
            if language == "ja":
                return PostMessageResponse(
                    response="関連する情報が見つかりませんでした。"
                )
            else:
                return PostMessageResponse(
                    response="No relevant information was found."
                )

        for hit in result.hits:
            logger.info(
                {
                    "event": "retrieved_relevant_information",
                    "score": hit.score,
                    "payload": hit.payload,
                }
            )

        response = generate_with_llm(question=message, contexts=result.contexts)
        logger.info({"event": "generate_with_llm", "response": response})
        return PostMessageResponse(response=response)
    except Exception as e:
        logger.exception("Failed to post a message")
        raise e
