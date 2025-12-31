from qdrant_client import QdrantClient

client = QdrantClient(host="host.docker.internal", port=6333)

COLLECTION_NAME = "tokyo_landprice_rag"
