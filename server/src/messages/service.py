from core.logger import logger
from messages.model import PostMessageRequest, PostMessageResponse
from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from core.qdrant import client, COLLECTION_NAME
from core.openai import embed, generate_with_llm


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
            return PostMessageResponse(response="関連する情報が見つかりませんでした。")

        contexts = []

        for hit in hits:
            text = hit.payload.get("text")
            logger.info(
                {
                    "event": "retrieved_relevant_information",
                    "score": hit.score,
                    "text": text,
                }
            )
            contexts.append(text)

        prompt = f"""
            以下の情報を参考に、質問に日本語で答えてください。
            情報に含まれない内容は推測せず、分かる範囲で説明してください。
            
            情報:
            {"\n".join(contexts)}
            
            質問:
            {body.message}
        """.strip()

        resp = generate_with_llm(prompt)

        return PostMessageResponse(response=resp)
    except Exception as e:
        logger.exception("Failed to post a message")
        raise e
