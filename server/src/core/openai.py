from openai import OpenAI
from .secret import secrets


openai = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))


def embed(text: str) -> list[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def generate_with_llm(prompt: str) -> str:
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content
