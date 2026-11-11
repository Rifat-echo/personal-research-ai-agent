
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI missing from .env")

try:
    with MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
    ) as client:
        client.admin.command("ping")
        print("MongoDB connected successfully!")

except Exception as error:
    print(f"Connection failed: {type(error).__name__}: {error}")
