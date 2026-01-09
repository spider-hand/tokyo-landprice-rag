from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.qdrant import client, COLLECTION_NAME, build_filter, build_geo_filter
from core.openai import embed, extract_intent, generate_with_llm


def post_message_service(event: APIGatewayProxyEventModel) -> PostMessageResponse:
    try:
        body = PostMessageRequest.model_validate_json(event.body)
        message = body.message
        lat = body.lat
        lon = body.lon
        is_point = body.is_point

        logger.info({"event": "validate_post_message_request", "body": body})

        query_filter = None

        if lat is not None and lon is not None:
            bbox_size = 1 if is_point else 500
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

        # Retrieve relevant information
        hits = client.query_points(
            collection_name=COLLECTION_NAME,
            query=embed(message),
            query_filter=query_filter,
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
