import json
from openai import OpenAI
from .secret import secrets
from .qdrant import SearchIntent
from .logger import logger


openai = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))


def embed(text: str) -> list[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def extract_intent(question: str) -> SearchIntent:
    prompt = f"""
        Extract search filters from the following user question as a JSON object.
        Return only valid JSON. Do not include explanations or markdown.

        Possible fields:
        - ward: Japanese municipality name WITHOUT administrative suffix.
                Remove 市, 区, 町, 村 from the name.
                Examples:
                    千代田区 → 千代田
                    武蔵野市 → 武蔵野
                    奥多摩町 → 奥多摩
                    檜原村 → 檜原
        - station: station name only (e.g. 半蔵門, 新宿)
        - usage: one of [住宅, 店舗, 事務所, 銀行, 旅館, 給油所, 工場, 倉庫, 農地, 山林, 医院, 空地, 作業所, 原野, 用材, 雑林]
        - time_to_station_max: maximum walking time to a station in minutes (integer)

        - require_max_price: true if the user is asking for the highest land price
        - require_min_price: true if the user is asking for the lowest land price
        - require_top_1_percent_price: true if the user is asking for the top 1% land price
        - require_bottom_1_percent_price: true if the user is asking for the bottom 1% land price

        - require_max_change_rate: true if the user is asking for the highest change rate
        - require_min_change_rate: true if the user is asking for the lowest change rate
        - require_top_1_percent_change_rate: true if the user is asking for the top 1% change rate
        - require_bottom_1_percent_change_rate: true if the user is asking for the bottom 1% change rate

        Do not include fields that are not mentioned in the question.
        If no fields apply, return an empty JSON object.

        Question:
        {question}
        """.strip()

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    content = resp.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(
            {"event": "json_decode_error", "content": content, "error": str(e)}
        )
        return {}


def generate_with_llm(question: str, contexts: list[str]) -> str:
    prompt = f"""
        System:
        You are a land price analysis assistant.
        First, determine whether the user's question is written in Japanese.
        Ignore numbers, coordinates, and symbols when determining the language.
        If it is Japanese, answer in Japanese.
        Otherwise, answer in English.
        Do not explain or mention the language decision in your answer.

        User:
        Explain the land price level and residential characteristics based on the provided information.
        Be concise and factual.
        Do not make up any information that is not present in the data.

        Contexts:
        {"\n\n".join(contexts)}

        Question:
        {question}
        """.strip()

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return resp.choices[0].message.content
