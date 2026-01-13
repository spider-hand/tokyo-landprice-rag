import boto3
import json
from functools import lru_cache
from typing import TypedDict
from .env import environment


class SecretDict(TypedDict):
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_HOST: str


@lru_cache(maxsize=1)
def get_secret() -> SecretDict:
    secret_name = f"tokyo-landprice-rag-{environment}"
    service_name = "secretsmanager"
    region_name = "ap-northeast-1"

    # localstack
    if environment == "localstack":
        client = boto3.client(
            service_name=service_name,
            region_name=region_name,
            endpoint_url="http://localstack-tokyo-landprice-rag:4566",
        )
    # prod
    else:
        client = boto3.client(
            service_name=service_name,
            region_name=region_name,
        )

    response = client.get_secret_value(SecretId=secret_name)
    secret_string = response["SecretString"]

    try:
        return json.loads(secret_string)
    except Exception as e:
        return {"error": str(e)}


secrets = get_secret()
