
import os
from datetime import timezone

import yfinance as yf
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "global_market_agent")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI missing from .env")


# Yahoo Finance index symbols
MARKETS = {
    "^GSPC": ("S&P 500", "United States", "USD"),
    "^FTSE": ("FTSE 100", "United Kingdom", "GBP"),
    "^N225": ("Nikkei 225", "Japan", "JPY"),
    "^NSEI": ("NIFTY 50", "India", "INR"),
    "^GDAXI": ("DAX", "Germany", "EUR"),
}


def fetch_and_store_market_data():
    with MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    ) as client:

        client.admin.command("ping")

        collection = client[DB_NAME]["market_prices"]

        collection.create_index(
            [("symbol", 1), ("date", 1)],
            unique=True,
        )

        for symbol, (market, country, currency) in MARKETS.items():
            print(f"\nFetching {market}...")

            try:
                data = yf.Ticker(symbol).history(
                    period="3mo",
                    interval="1d",
                    auto_adjust=True,
                )

                if data.empty:
                    print("No data returned.")
                    continue

                operations = []

                for date, row in data.iterrows():
                    close = row["Close"]

                    if close != close:
                        continue

                    # Normalize the timestamp to a UTC date.
                    # Daily index bars are indexed by exchange date.
                    market_date = date.date()

                    from datetime import datetime
                    utc_date = datetime(
                        market_date.year,
                        market_date.month,
                        market_date.day,
                        tzinfo=timezone.utc,
                    )

                    record = {
                        "symbol": symbol,
                        "market": market,
                        "country": country,
                        "date": utc_date,
                        "close": float(close),
                        "currency": currency,
                        "source": "yfinance",
                    }

                    operations.append(
                        UpdateOne(
                            {
                                "symbol": symbol,
                                "date": utc_date,
                            },
                            {"$set": record},
                            upsert=True,
                        )
                    )

                if operations:
                    result = collection.bulk_write(operations)

                    print(
                        f"Processed {len(operations)} daily prices. "
                        f"Inserted {result.upserted_count}, "
                        f"updated {result.modified_count}."
                    )

            except Exception as error:
                print(
                    f"Error fetching {symbol}: "
                    f"{type(error).__name__}: {error}"
                )

        print("\nMarket data collection finished!")


if __name__ == "__main__":
    fetch_and_store_market_data()
