from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MongoDB URL from .env
mongo_uri = os.getenv("MONGO_DBURL")

client = MongoClient(mongo_uri)

db = client["movies_db"]
collection = db["movies_db"]

movies = list(collection.find())