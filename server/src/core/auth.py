from aws_lambda_powertools.utilities.typing import LambdaContext
from core.logger import dynamic_inject_lambda_context, logger


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
}


@dynamic_inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        policy = generate_policy("demo_user_id", "Allow", "*")

        return policy

    except Exception as e:
        logger.exception("Authentication error")
        logger.info(
            {
                "event": "authentication_failed",
                "error": str(e),
            }
        )
        policy = generate_policy("demo_user_id", "Deny", "*")
        return policy


def generate_policy(principal_id: str, effect: str, resource: str) -> dict:
    policy_document = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        },
        "context": {
            "uid": principal_id if effect == "Allow" else None,
            "authorized": effect == "Allow",
        },
    }

    return policy_document
