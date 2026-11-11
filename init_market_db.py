
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv(
    "MONGODB_DB",
    "global_market_agent",
)

if not MONGODB_URI:
    raise ValueError("MONGODB_URI missing from .env")


def initialize_market_database():
    with MongoClient(MONGODB_URI) as client:
        database = client[DB_NAME]
        collection = database["market_prices"]

        # Prevent duplicate records for the same market/date.
        collection.create_index(
            [("symbol", 1), ("date", 1)],
            unique=True,
        )

        # This is test data, NOT a live market price.
        sample_record = {
            "symbol": "^GSPC",
            "market": "S&P 500",
            "country": "United States",
            "date": datetime(
                2026, 1, 2, tzinfo=timezone.utc
            ),
            "close": 6000.0,
            "currency": "USD",
            "source": "sample_data",
        }

        collection.update_one(
            {
                "symbol": sample_record["symbol"],
                "date": sample_record["date"],
            },
            {"$set": sample_record},
            upsert=True,
        )

        print("Market database initialized!")
        print(f"Database: {DB_NAME}")
        print("Collection: market_prices")
        print("Sample record inserted successfully.")


if __name__ == "__main__":
    initialize_market_database()
