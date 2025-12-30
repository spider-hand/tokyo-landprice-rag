import boto3
import json
import os
from functools import lru_cache
from typing import TypedDict


class SecretDict(TypedDict):
    test: str


@lru_cache(maxsize=1)
def get_secret() -> SecretDict:
    environment = os.getenv("Environment", "localstack")

    secret_name = f"tokyo-landprice-rag-{environment}"
    service_name = "secretsmanager"
    region_name = "ap-northeast-1"

    # localstack
    client = boto3.client(
        service_name=service_name,
        region_name=region_name,
        endpoint_url="http://localstack-main:4566",
    )

    response = client.get_secret_value(SecretId=secret_name)
    secret_string = response["SecretString"]

    try:
        return json.loads(secret_string)
    except Exception as e:
        return {"error": str(e)}
