from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    GeoBoundingBox,
    GeoPoint,
    ScoredPoint,
)
from typing import TypedDict, Optional
from .secret import secrets
from .env import environment

# script
if environment is None:
    client = QdrantClient(host="localhost", port=6333)
# localstack
elif environment == "localstack":
    client = QdrantClient(host="host.docker.internal", port=6333)
# prod
else:
    client = QdrantClient(
        api_key=secrets["QDRANT_API_KEY"],
        host=secrets["QDRANT_HOST"],
        port=443,
        check_compatibility=False,
    )

COLLECTION_NAME = "tokyo_landprice_rag"

METERS_PER_DEG_LAT = 111000
METERS_PER_DEG_LON = 91000


@dataclass
class RetrievalResult:
    contexts: list[str]
    hits: list[ScoredPoint]


class SearchIntent(TypedDict, total=False):
    ward: str
    station: str
    usage: str
    time_to_station_max: int

    require_max_price: bool
    require_min_price: bool
    require_top_1_percent_price: bool
    require_bottom_1_percent_price: bool

    require_max_change_rate: bool
    require_min_change_rate: bool
    require_top_1_percent_change_rate: bool
    require_bottom_1_percent_change_rate: bool


def build_filter(intent: SearchIntent) -> Optional[Filter]:
    must: list[FieldCondition] = []

    def require_true(field_name: str) -> None:
        must.append(
            FieldCondition(
                key=field_name,
                match=MatchValue(value=True),
            )
        )

    if intent.get("ward"):
        must.append(
            FieldCondition(
                key="ward",
                match=MatchValue(value=intent["ward"]),
            )
        )

    if intent.get("station"):
        must.append(
            FieldCondition(
                key="station",
                match=MatchValue(value=intent["station"]),
            )
        )

    if intent.get("usage"):
        must.append(
            FieldCondition(
                key="usage",
                match=MatchValue(value=intent["usage"]),
            )
        )

    if intent.get("time_to_station_max"):
        must.append(
            FieldCondition(
                key="time_to_station",
                range=Range(lte=intent["time_to_station_max"]),
            )
        )

    if intent.get("require_max_price"):
        require_true("is_max_price")

    if intent.get("require_min_price"):
        require_true("is_min_price")

    if intent.get("require_top_1_percent_price"):
        require_true("is_top_1_percent_price")

    if intent.get("require_bottom_1_percent_price"):
        require_true("is_bottom_1_percent_price")

    if intent.get("require_max_change_rate"):
        require_true("is_max_change_rate")

    if intent.get("require_min_change_rate"):
        require_true("is_min_change_rate")

    if intent.get("require_top_1_percent_change_rate"):
        require_true("is_top_1_percent_change_rate")

    if intent.get("require_bottom_1_percent_change_rate"):
        require_true("is_bottom_1_percent_change_rate")

    if not must:
        return None

    return Filter(must=must)


def build_geo_filter(lat: float, lon: float, bbox_size_meters: float = 500) -> Filter:
    half_size_lat = (bbox_size_meters / 2) / METERS_PER_DEG_LAT
    half_size_lon = (bbox_size_meters / 2) / METERS_PER_DEG_LON

    return Filter(
        must=[
            FieldCondition(
                key="location",
                geo_bounding_box=GeoBoundingBox(
                    top_left=GeoPoint(lat=lat + half_size_lat, lon=lon - half_size_lon),
                    bottom_right=GeoPoint(
                        lat=lat - half_size_lat, lon=lon + half_size_lon
                    ),
                ),
            ),
        ]
    )


def retrieve_contexts(
    vector: list[float], query_filter: Optional[Filter], limit: int = 5
) -> RetrievalResult:
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=query_filter,
        limit=limit,
    ).points

    contexts = [hit.payload["semantic_text"] for hit in hits]
    return RetrievalResult(contexts=contexts, hits=hits)
