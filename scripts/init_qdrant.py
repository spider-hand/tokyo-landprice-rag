import os
import json
from qdrant_client import models, QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
from typing import TypedDict
from tqdm import tqdm


class PropsDict(TypedDict):
    price: int
    change_rate: float
    ward: str
    address: str
    usage: str
    usage_detail: str
    surrounding_detail: str
    station: str
    distance_to_station: int


# Load environment variables
load_dotenv()

# Configuration
COLLECTION_NAME = "tokyo_landprice_rag"
GEOJSON_PATH = "data/L01-25_13.geojson"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

EMBED_MODEL = "text-embedding-3-small"
VECTOR_SIZE = 1536
BATCH_SIZE = 2048

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def build_price_tier_text(price: int) -> str:
    if price < 228800:
        return "非常に低い水準"
    elif price < 409600:
        return "低い水準"
    elif price < 666400:
        return "平均的な水準"
    elif price < 1250000:
        return "高い水準"
    else:
        return "非常に高い水準"


def get_price_tier(price: int) -> int:
    if price < 228800:
        return 1
    elif price < 409600:
        return 2
    elif price < 666400:
        return 3
    elif price < 1250000:
        return 4
    else:
        return 5


def build_distance_to_station_tier_text(distance: int) -> str:
    if distance < 252:
        return "駅から非常に近い"
    elif distance < 484:
        return "駅から近い"
    elif distance < 750:
        return "駅からやや近い"
    elif distance < 1200:
        return "駅からやや遠い"
    else:
        return "駅から非常に遠い"


def get_distance_to_station_tier(distance: int) -> int:
    if distance < 252:
        return 1
    elif distance < 484:
        return 2
    elif distance < 750:
        return 3
    elif distance < 1200:
        return 4
    else:
        return 5


def build_knowledge_base(p: PropsDict) -> str:
    return (
        f"東京都{p['ward']}{p['address']}の土地は、{p['usage']}（{p['usage_detail']}）に分類され、"
        f"周辺環境は{p['surrounding_detail']}です。最寄り駅は{p['station']}で、"
        f"駅からの距離は約{p['distance_to_station']}メートルです。"
        f"土地の価格は1平方メートルあたり約{p['price']}円で、"
        f"これは{build_price_tier_text(p['price'])}、"
        f"駅からの距離は{build_distance_to_station_tier_text(p['distance_to_station'])}です。"
    )


def embed_batch(texts: list[str]) -> list[list[float]]:
    response = openai.embeddings.create(
        input=texts,
        model=EMBED_MODEL,
    )
    return [item.embedding for item in response.data]


def main():
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    features = geojson["features"]
    print(f"Processing {len(features)} features...")

    # @see: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2025.html

    # Prepare data items
    data_items = []
    for feature in tqdm(features, desc="Preparing data"):
        prop = feature["properties"]
        lng, lat = feature["geometry"]["coordinates"]

        p = {
            "price": prop["L01_008"],
            "change_rate": prop["L01_009"],
            "ward": prop["L01_024"],
            "address": prop["L01_025"],
            "usage": prop["L01_028"],
            "usage_detail": prop["L01_029"],
            "surrounding_detail": prop["L01_047"],
            "station": prop["L01_048"],
            "distance_to_station": prop["L01_050"],
        }

        text = build_knowledge_base(p)
        data_items.append((text, p, lat, lng))

    # Batch embed texts
    all_vectors = []

    texts = [item[0] for item in data_items]
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding batches"):
        batch_texts = texts[i : i + BATCH_SIZE]
        vectors = embed_batch(batch_texts)
        all_vectors.extend(vectors)

    # Create points with embedded vectors
    points = []
    for idx, (text, p, lat, lng) in enumerate(tqdm(data_items, desc="Creating points")):
        point = models.PointStruct(
            id=idx + 1,
            vector=all_vectors[idx],
            payload={
                "text": text,
                "ward": p["ward"],
                "station": p["station"],
                "lat": lat,
                "lng": lng,
                "price_tier": get_price_tier(p["price"]),
                "distance_to_station_tier": get_distance_to_station_tier(
                    p["distance_to_station"]
                ),
            },
        )
        points.append(point)

    print(f"Uploading {len(points)} points to Qdrant...")
    client.upload_points(
        collection_name=COLLECTION_NAME,
        points=points,
    )
    print(f"Successfully uploaded {len(points)} points to Qdrant.")


if __name__ == "__main__":
    main()
