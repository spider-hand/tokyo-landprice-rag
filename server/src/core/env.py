import os
from typing import Literal, cast

Environment = Literal["localstack", "prod"]

raw_environment = os.getenv("Environment")

if raw_environment is None:
    environment = None
elif raw_environment in ("localstack", "prod"):
    environment = cast(Environment, raw_environment)
else:
    raise ValueError(f"Invalid Environment value: {raw_environment}")
