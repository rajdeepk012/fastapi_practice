# Import the FastAPI class from fastapi library
from fastapi import FastAPI, HTTPException, status
# Import BaseModel from pydantic for data validation
from pydantic import BaseModel
# Import datetime for timestamps
from datetime import datetime
# Import typing for type hints
from typing import List

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

# ========== CHATBOT SECTION ==========

# In-memory storage for conversation history
# Format: {session_id: [list of message exchanges]}
conversation_history = {}

# Chatbot request model
class ChatRequest(BaseModel):
    user_message: str            # User's input message
    user_name: str = "User"      # Optional user name (defaults to "User")
    session_id: str = "default"  # Session ID to track conversations

# Chatbot response model
class ChatResponse(BaseModel):
    bot_reply: str               # Bot's response
    user_message: str            # Echo back user's message
    user_name: str               # User's name
    session_id: str              # Session identifier
    timestamp: str               # When the message was sent

# Model for conversation history entry
class ConversationEntry(BaseModel):
    user_message: str
    bot_reply: str
    user_name: str
    timestamp: str

# Simple chatbot logic function
def chatbot_reply(user_input: str) -> str:
    """
    Rule-based chatbot that matches patterns and returns responses
    """
    # Convert to lowercase for matching
    message = user_input.lower().strip()

    # Greeting patterns
    if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
        return "Hi there! How can I help you today?"

    # Name questions
    if "your name" in message or "who are you" in message:
        return "I'm FastAPI Bot, your friendly assistant built with FastAPI!"

    # FastAPI questions
    if "fastapi" in message:
        return "FastAPI is a modern, fast Python web framework for building APIs. It's awesome!"

    # How are you
    if "how are you" in message:
        return "I'm doing great! Thanks for asking. How can I assist you?"

    # Help requests
    if "help" in message:
        return "I can chat with you! Try asking me about FastAPI, say hello, or ask my name!"

    # Default response for unknown inputs
    return "Interesting! I'm still learning. Can you try asking something else?"

# Chatbot endpoint with history tracking
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chatbot endpoint that processes messages and saves conversation history
    """
    # Get bot's reply using chatbot logic
    bot_response = chatbot_reply(request.user_message)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create conversation entry
    entry = ConversationEntry(
        user_message=request.user_message,
        bot_reply=bot_response,
        user_name=request.user_name,
        timestamp=timestamp
    )

    # Save to history (create session if doesn't exist)
    if request.session_id not in conversation_history:
        conversation_history[request.session_id] = []

    conversation_history[request.session_id].append(entry)

    # Return structured response
    return ChatResponse(
        bot_reply=bot_response,
        user_message=request.user_message,
        user_name=request.user_name,
        session_id=request.session_id,
        timestamp=timestamp
    )

# Get conversation history endpoint
@app.get("/chat/history/{session_id}", response_model=List[ConversationEntry])
def get_history(session_id: str):
    """
    Retrieve conversation history for a specific session
    """
    # Check if session exists
    if session_id not in conversation_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No conversation history found for session '{session_id}'"
        )

    # Return the conversation history
    return conversation_history[session_id]
