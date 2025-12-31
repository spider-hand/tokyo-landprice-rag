from qdrant_client import models, QdrantClient

client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "tokyo_landprice_rag"

if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=3,
            distance=models.Distance.COSINE,
        ),
    )


client.upload_points(
    collection_name=COLLECTION_NAME,
    points=[
        models.PointStruct(
            id=1,
            vector=[0.1, 0.2, 0.3],
            payload={
                "area": "Minato",
                "text": "Minato ward has some of the highest land prices in Tokyo.",
            },
        ),
        models.PointStruct(
            id=2,
            vector=[0.4, 0.5, 0.6],
            payload={
                "area": "Shibuya",
                "text": "Shibuya ward is known for its bustling commercial areas and high land prices.",
            },
        ),
    ],
)

print(f"Initialized Qdrant collection '{COLLECTION_NAME}' with sample data.")
