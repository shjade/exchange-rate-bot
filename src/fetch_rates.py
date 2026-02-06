import os
import json
import urllib.request
from datetime import datetime, timezone

API_KEY = os.getenv("EXCHANGE_API_KEY")
FROM_CURRENCY = os.getenv("FROM_CURRENCY", "USD")
TO_CURRENCY = os.getenv("TO_CURRENCY", "KRW")
OUT_PATH = os.getenv("OUT_PATH", "data/exchange_rates.json")

def fetch_rate_alpha_vantage(api_key: str, from_cur: str, to_cur: str) -> dict:
    url = (
        "https://www.alphavantage.co/query"
        f"?function=CURRENCY_EXCHANGE_RATE&from_currency={from_cur}"
        f"&to_currency={to_cur}&apikey={api_key}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        data = json.loads(raw)

    # API 에러/제한 등
    if "Error Message" in data or "Information" in data or "Note" in data:
        raise RuntimeError(f"API error/limit: {data}")

    rate_block = data.get("Realtime Currency Exchange Rate", {})
    if not rate_block:
        raise RuntimeError(f"Unexpected response: {data}")

    return {
        "provider": "AlphaVantage",
        "from": from_cur,
        "to": to_cur,
        "rate": float(rate_block["5. Exchange Rate"]),
        "as_of": rate_block.get("6. Last Refreshed"),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    }

def main():
    if not API_KEY:
        raise SystemExit("Missing EXCHANGE_API_KEY environment variable")

    result = fetch_rate_alpha_vantage(API_KEY, FROM_CURRENCY, TO_CURRENCY)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Updated {OUT_PATH}: {result['from']}->{result['to']} = {result['rate']}")

if __name__ == "__main__":
    main()
