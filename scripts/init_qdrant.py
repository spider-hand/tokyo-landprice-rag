import os
from qdrant_client import models, QdrantClient
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "tokyo_landprice_rag"


def embed(text: str) -> list[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


if client.collection_exists(collection_name=COLLECTION_NAME):
    client.delete_collection(collection_name=COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size=1536,
        distance=models.Distance.COSINE,
    ),
)


client.upload_points(
    collection_name=COLLECTION_NAME,
    points=[
        models.PointStruct(
            id=1,
            vector=embed(
                text="Minato ward has some of the highest land prices in Tokyo."
            ),
            payload={
                "area": "Minato",
            },
        ),
        models.PointStruct(
            id=2,
            vector=embed(
                text="Shibuya ward is known for its bustling commercial areas and high land prices."
            ),
            payload={
                "area": "Shibuya",
            },
        ),
    ],
)

print(f"Initialized Qdrant collection '{COLLECTION_NAME}' with sample data.")
