import os
from typing import Literal, cast

Environment = Literal["localstack", "prod"]

raw_environment = os.getenv("Environment", "localstack")

if raw_environment not in ("localstack", "prod"):
    raise ValueError(f"Invalid Environment value: {raw_environment}")

environment = cast(Environment, raw_environment)
