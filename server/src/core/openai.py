from openai import OpenAI
from .secret import secrets


openai = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))


def embed(text: str) -> list[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding
