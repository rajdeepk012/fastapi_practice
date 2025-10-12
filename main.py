# Import the FastAPI class from fastapi library
from fastapi import FastAPI
# Import BaseModel from pydantic for data validation
from pydantic import BaseModel

# Create an instance of FastAPI application
app = FastAPI()

# Pydantic model: defines the structure and types for request body
class Message(BaseModel):
    text: str           # Message text (required)
    user_name: str      # Sender's name (required)
    timestamp: int = 0  # Unix timestamp (optional, default 0)

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}

# Path parameter: {user_id} is a dynamic variable in the URL
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # user_id is extracted from URL and validated as integer
    return {"user_id": user_id, "message": f"Hello user {user_id}"}

# Query parameters: variables passed after ? in URL
@app.get("/search")
def search_items(q: str):
    # q is extracted from URL query string: /search?q=laptop
    return {"query": q, "message": f"Searching for: {q}"}

# Optional query parameter with default value
@app.get("/items")
def read_items(skip: int = 0, limit: int = 10):
    # skip and limit are optional - have default values
    # /items → skip=0, limit=10
    # /items?skip=5 → skip=5, limit=10
    # /items?skip=5&limit=20 → skip=5, limit=20
    return {"skip": skip, "limit": limit}

# POST request with request body using Pydantic model
@app.post("/messages")
def create_message(message: Message):
    # message parameter automatically validated against Message model
    # FastAPI extracts JSON from request body and validates it
    return {
        "status": "received",
        "message_text": message.text,
        "from": message.user_name,
        "timestamp": message.timestamp
    }
