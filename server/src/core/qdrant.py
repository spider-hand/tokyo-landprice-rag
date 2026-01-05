from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range
from typing import TypedDict, Optional

client = QdrantClient(host="host.docker.internal", port=6333)

COLLECTION_NAME = "tokyo_landprice_rag"


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

    semantic_search: bool


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

    if intent.get("land_usage"):
        must.append(
            FieldCondition(
                key="land_usage",
                match=MatchValue(value=intent["land_usage"]),
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
