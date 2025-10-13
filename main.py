# Import the FastAPI class from fastapi library
from fastapi import FastAPI, HTTPException, status
# Import BaseModel from pydantic for data validation
from pydantic import BaseModel

# Create an instance of FastAPI application
app = FastAPI()

# Pydantic model: defines the structure and types for request body
class Message(BaseModel):
    text: str           # Message text (required)
    user_name: str      # Sender's name (required)
    timestamp: int = 0  # Unix timestamp (optional, default 0)

# Response model: defines what the API returns
class MessageResponse(BaseModel):
    id: int                    # Message ID
    status: str                # Status message
    message_text: str          # The message content
    from_user: str             # Sender's name
    timestamp: int             # When message was received

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}

# Path parameter with error handling
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # Simulate checking if user exists (in real app: check database)
    # For demo: only users 1-100 exist
    if user_id < 1 or user_id > 100:
        # Raise 404 error if user doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # User exists, return data
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

# POST request with response model and status code
@app.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: Message):
    # message parameter automatically validated against Message model
    # In real app: save to database and get real ID
    # For demo: generate fake ID
    fake_id = 42

    # Return response matching MessageResponse model
    return MessageResponse(
        id=fake_id,
        status="created",
        message_text=message.text,
        from_user=message.user_name,
        timestamp=message.timestamp
    )
