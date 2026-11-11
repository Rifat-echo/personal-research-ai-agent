
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "global_market_agent")

MARKETS = {
    "SP500": "^GSPC",
    "FTSE100": "^FTSE",
    "NIKKEI225": "^N225",
    "NIFTY50": "^NSEI",
    "DAX": "^GDAXI",
}


def get_market_trend(
    market: str,
    days: int = 30,
) -> dict:
    """Analyze historical market prices stored in MongoDB."""

    market = market.strip().upper()

    if market not in MARKETS:
        return {
            "error": "Unsupported market.",
            "supported_markets": list(MARKETS.keys()),
        }

    if not isinstance(days, int) or not 1 <= days <= 365:
        return {"error": "Days must be between 1 and 365."}

    if not MONGODB_URI:
        return {"error": "MONGODB_URI is missing."}

    symbol = MARKETS[market]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        with MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        ) as client:
            collection = client[DB_NAME]["market_prices"]

            records = list(
                collection.find(
                    {
                        "symbol": symbol,
                        "source": "yfinance",
                    },
                    {
                        "_id": 0,
                        "date": 1,
                        "close": 1,
                        "currency": 1,
                    },
                ).sort("date", 1)
            )

    except Exception as error:
        return {
            "error": f"Database query failed: {type(error).__name__}"
        }

    if not records:
        return {"error": "No market data available."}

    # Calculate the trend using the latest stored date.
    latest_date = records[-1]["date"]
    window_start = latest_date - timedelta(days=days)

    window = [
        record
        for record in records
        if record["date"] >= window_start
    ]

    if len(window) < 2:
        return {
            "error": "Not enough records to calculate a trend."
        }

    first_price = window[0]["close"]
    latest_price = window[-1]["close"]

    percentage_change = (
        (latest_price - first_price) / first_price
    ) * 100

    prices = [record["close"] for record in records]

    ma5 = (
        sum(prices[-5:]) / 5
        if len(prices) >= 5
        else None
    )

    ma20 = (
        sum(prices[-20:]) / 20
        if len(prices) >= 20
        else None
    )

    trend = (
        "Upward" if percentage_change > 0
        else "Downward" if percentage_change < 0
        else "Flat"
    )

    return {
        "market": market,
        "symbol": symbol,
        "period_days": days,
        "start_date": window[0]["date"].date().isoformat(),
        "latest_date": latest_date.date().isoformat(),
        "currency": window[-1]["currency"],
        "start_close": round(first_price, 2),
        "latest_close": round(latest_price, 2),
        "percentage_change": round(percentage_change, 2),
        "moving_average_5": (
            round(ma5, 2) if ma5 is not None else None
        ),
        "moving_average_20": (
            round(ma20, 2) if ma20 is not None else None
        ),
        "trend": trend,
        "observations": len(window),
        "source": "yfinance",
    }


if __name__ == "__main__":
    result = get_market_trend("SP500", 30)
    print(result)
