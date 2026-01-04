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
        以下のユーザーの質問から検索条件をJSON形式で抽出してください。
        必ず有効なJSON形式のみを返してください。余分な説明やマークダウンは含めないでください。

        抽出対象:
        - ward 市区町村は含めない（例: 千代田)
        - station 駅名のみ（例: 半蔵門)
        - usage 住宅, 店舗, 事務所, 銀行, 旅館, 給油所, 工場, 倉庫, 農地, 山林, 医院, 空地, 作業所, 原野, 用材, 雑林のいずれか

        - require_max_price: 最高価格を検索条件に含めるなら true
        - require_min_price: 最低価格を検索条件に含めるなら true
        - require_top_1_percent_price: 価格の上位1%を検索条件に含めるなら true
        - require_bottom_1_percent_price: 価格の下位1%を検索条件に含めるなら true

        - require_max_change_rate: 最高変動率を検索条件に含めるなら true
        - require_min_change_rate: 最低変動率を検索条件に含めるなら true
        - require_top_1_percent_change_rate: 変動率の上位1%を検索条件に含めるなら true
        - require_bottom_1_percent_change_rate: 変動率の下位1%を検索条件に含めるなら true

        - semantic_search: 意味検索が必要なら true

        質問に該当しない項目は含めないでください。
        該当する項目がない場合は空のJSONオブジェクトを返してください。

        質問:
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
        以下の情報を参考に、質問に答えてください。
        質問文が日本語でない場合は、英語で回答してください。
        事実に基づいて簡潔に説明してください。
        推測はしないでください。

        情報:
        {"\n\n".join(contexts)}

        質問:
        {question}
        """.strip()

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return resp.choices[0].message.content
