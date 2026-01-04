import os
import json
import numpy as np
from qdrant_client import models, QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
from typing import TypedDict
from tqdm import tqdm
import mapclassify


class KnowledgeDict(TypedDict):
    price_tier: int
    change_rate_tier: int
    ward: str
    address: str
    usage: str
    usage_detail: str
    surrounding_detail: str
    station: str
    distance_to_station_tier: int


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


def build_embedding_input(k: KnowledgeDict) -> str:

    def build_price_tier_text(tier: int) -> str:
        return {
            5: "地価が非常に高いエリアです。",
            4: "地価が高いエリアです。",
            3: "地価は平均的な水準です。",
            2: "地価は比較的抑えられています。",
            1: "地価が低めのエリアです。",
        }.get(tier, "")

    def build_change_rate_tier_text(tier: int) -> str:
        return {
            5: "地価は大きく上昇傾向にあります。",
            4: "地価は上昇傾向にあります。",
            3: "地価は比較的安定しています。",
            2: "地価はやや下落傾向です。",
            1: "地価は下落傾向にあります。",
        }.get(tier, "")

    def build_distance_to_station_tier_text(tier: int) -> str:
        return {
            1: "駅から非常に近く、利便性の高い立地です。",
            2: "駅から近く、徒歩圏内の立地です。",
            3: "駅まで徒歩でアクセス可能な立地です。",
            4: "駅からやや距離があります。",
            5: "駅から距離があり、落ち着いた立地です。",
        }.get(tier, "")

    parts: list[str] = []

    # Location
    parts.append(f"この土地は東京都{k['ward']}に位置しています。")
    parts.append(f"住所は{k['address']}です。")

    # Station
    parts.append(f"最寄り駅は{k['station']}です。")
    parts.append(build_distance_to_station_tier_text(k["distance_to_station_tier"]))

    # Usage
    parts.append(f"土地は{k['usage']}として利用されています。")
    parts.append(f"具体的には{k['usage_detail']}として利用されています。")
    parts.append(f"周辺環境は{k['surrounding_detail']}となっています。")

    # Value
    parts.append(build_price_tier_text(k["price_tier"]))
    parts.append(build_change_rate_tier_text(k["change_rate_tier"]))

    return "\n".join(parts)


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

    # Prepare data
    prices = np.array([f["properties"]["L01_008"] for f in features])
    change_rates = np.array([f["properties"]["L01_009"] for f in features])
    distances = np.array([f["properties"]["L01_050"] for f in features])

    # Create classifiers using Quantiles (5 classes)
    price_classifier = mapclassify.Quantiles(prices, k=5)
    change_rate_classifier = mapclassify.Quantiles(change_rates, k=5)
    distance_classifier = mapclassify.Quantiles(distances, k=5)

    price_min, price_max = prices.min(), prices.max()
    change_rate_min, change_rate_max = change_rates.min(), change_rates.max()

    price_top_1 = np.percentile(prices, 99)
    price_bottom_1 = np.percentile(prices, 1)

    change_rate_top_1 = np.percentile(change_rates, 99)
    change_rate_bottom_1 = np.percentile(change_rates, 1)

    data_items = []

    for idx, feature in enumerate(tqdm(features, desc="Preparing data")):
        prop = feature["properties"]
        lng, lat = feature["geometry"]["coordinates"]
        price = prop["L01_008"]
        change_rate = prop["L01_009"]
        ward = prop["L01_024"]
        usage = prop["L01_028"]
        station = prop["L01_048"]
        distance_to_station = prop["L01_050"]

        price_tier = int(price_classifier.yb[idx]) + 1
        change_rate_tier = int(change_rate_classifier.yb[idx]) + 1
        distance_tier = int(distance_classifier.yb[idx]) + 1

        knowledge = {
            "price_tier": price_tier,
            "change_rate_tier": change_rate_tier,
            "ward": ward,
            "address": prop["L01_025"],
            "usage": usage,
            "usage_detail": prop["L01_029"],
            "surrounding_detail": prop["L01_047"],
            "station": station,
            "distance_to_station_tier": distance_tier,
        }

        embedding_input = build_embedding_input(knowledge)

        payload = {
            "price": price,
            "price_tier": knowledge["price_tier"],
            "price_percentile": float((prices < price).sum() / len(prices) * 100),
            "is_top_1_percent_price": bool(price >= price_top_1),
            "is_bottom_1_percent_price": bool(price <= price_bottom_1),
            "is_max_price": bool(price == price_max),
            "is_min_price": bool(price == price_min),
            "change_rate": change_rate,
            "change_rate_tier": knowledge["change_rate_tier"],
            "change_rate_percentile": float(
                (change_rates < change_rate).sum() / len(change_rates) * 100
            ),
            "is_top_1_percent_change_rate": bool(change_rate >= change_rate_top_1),
            "is_bottom_1_percent_change_rate": bool(change_rate <= change_rate_bottom_1),
            "is_max_change_rate": bool(change_rate == change_rate_max),
            "is_min_change_rate": bool(change_rate == change_rate_min),
            "ward": ward,
            "station": station,
            "usage": usage,
            "distance_to_station": distance_to_station,
            "distance_to_station_tier": knowledge["distance_to_station_tier"],
            "lat": lat,
            "lng": lng,
            "semantic_text": embedding_input,
        }

        data_items.append(payload)

    # Batch embedding inputs
    all_vectors = []

    embedding_inputs = [item["semantic_text"] for item in data_items]
    for i in tqdm(
        range(0, len(embedding_inputs), BATCH_SIZE), desc="Embedding batches"
    ):
        batch_texts = embedding_inputs[i : i + BATCH_SIZE]
        vectors = embed_batch(batch_texts)
        all_vectors.extend(vectors)

    # Create points with embeddings and payloads
    points = []

    for idx, payload in enumerate(
        tqdm(data_items, desc="Creating points")
    ):
        vector = all_vectors[idx]
        point = models.PointStruct(
            id=idx,
            vector=vector,
            payload=payload,
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
