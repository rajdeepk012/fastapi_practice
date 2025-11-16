# MongoDB Connection Configuration using Motor (Async Driver)
# Motor is the async MongoDB driver for Python, works with FastAPI

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MongoDB Connection URL
# Format: mongodb://host:port
# localhost:27017 is the default MongoDB server address
MONGODB_URL = "mongodb://localhost:27017"

# Maximum number of connections in the connection pool
# Connection pool = pre-made connections ready to use (faster!)
MAX_CONNECTIONS = 10
MIN_CONNECTIONS = 1

# Create Motor client (async MongoDB client)
# This is like creating the engine in SQLAlchemy
client: Optional[AsyncIOMotorClient] = None

# Database reference
# This will point to our 'chatbot_db' database
database = None


def connect_to_mongo():
    """
    Connect to MongoDB when the application starts.
    Called once at startup.
    """
    global client, database

    print("Connecting to MongoDB...")

    # Create async MongoDB client
    client = AsyncIOMotorClient(
        MONGODB_URL,
        maxPoolSize=MAX_CONNECTIONS,
        minPoolSize=MIN_CONNECTIONS
    )

    # Get database reference
    # This is like "USE chatbot_db" in MySQL
    database = client.chatbot_db

    print("Connected to MongoDB!")


def close_mongo_connection():
    """
    Close MongoDB connection when the application shuts down.
    Called once at shutdown.
    """
    global client

    print("Closing MongoDB connection...")

    if client:
        client.close()

    print("MongoDB connection closed!")


# Helper function to get database
def get_database():
    """
    Get database instance.
    Used in FastAPI endpoints with Depends().
    """
    return database
