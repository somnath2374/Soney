from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection

MONGO_URI = "mongodb://localhost:27017/soney"
DATABASE_NAME = "soney"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
users_collection: Collection = db["users"]
posts_collection: Collection = db["posts"]
comments_collection: Collection = db["comments"]
likes_collection: Collection = db["likes"]
chats_collection: Collection = db["chats"]
honeytraps_collection = db["honeytraps"]
logs_collection = db["logs"]
detected_collection=db["detected"]
