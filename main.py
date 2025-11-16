# FastAPI application with complete database integration
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

# Import MySQL database modules
import crud #queries
import schemas #api validation
import models #db table map
from database import engine, get_db

# Import MongoDB modules
import mongo_crud
import mongo_models
from mongodb import connect_to_mongo, close_mongo_connection, get_database

# Import for in-memory chatbot (from previous sessions)
from datetime import datetime

# Create database tables (if they don't exist)
# Note: In production, use Alembic migrations instead
models.Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Chatbot API",
    description="FastAPI application with MySQL and MongoDB integration",
    version="3.0.0"
)

# MongoDB Lifecycle Events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB when app starts"""
    connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection when app shuts down"""
    close_mongo_connection()

# ========== ROOT ENDPOINT ==========

@app.get("/")
def read_root():
    """Root endpoint - API info"""
    return {
        "message": "Chatbot API with Database Integration",
        "version": "2.0.0",
        "endpoints": {
            "users": "/users",
            "conversations": "/conversations",
            "chatbot": "/chat",
            "docs": "/docs"
        }
    }

# ========== USER ENDPOINTS ==========

@app.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user

    - **username**: User's username (required)
    - **email**: User's email address (required, unique)
    """
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of users with pagination

    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum number of users to return (default: 100)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID

    - **user_id**: The ID of the user to retrieve
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing user

    - **user_id**: The ID of the user to update
    - **username**: New username (optional)
    - **email**: New email (optional)
    """
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user

    - **user_id**: The ID of the user to delete
    """
    deleted = crud.delete_user(db, user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None  # 204 No Content


# ========== CONVERSATION ENDPOINTS ==========

@app.post("/conversations", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation

    - **user_id**: ID of the user (must exist)
    - **message**: User's message
    - **bot_reply**: Bot's reply (optional)
    """
    # Verify user exists
    user = crud.get_user(db, user_id=conversation.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {conversation.user_id} not found"
        )

    return crud.create_conversation(db=db, conversation=conversation)


@app.get("/conversations", response_model=List[schemas.Conversation])
def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all conversations with pagination

    - **skip**: Number of conversations to skip (default: 0)
    - **limit**: Maximum number of conversations to return (default: 100)
    """
    conversations = crud.get_conversations(db, skip=skip, limit=limit)
    return conversations


@app.get("/conversations/{conversation_id}", response_model=schemas.Conversation)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get a specific conversation by ID

    - **conversation_id**: The ID of the conversation to retrieve
    """
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return conversation


@app.get("/users/{user_id}/conversations", response_model=List[schemas.Conversation])
def get_user_conversations(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all conversations for a specific user

    - **user_id**: The ID of the user
    - **skip**: Number of conversations to skip (default: 0)
    - **limit**: Maximum number of conversations to return (default: 100)
    """
    # Verify user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    conversations = crud.get_user_conversations(db, user_id=user_id, skip=skip, limit=limit)
    return conversations


@app.put("/conversations/{conversation_id}", response_model=schemas.Conversation)
def update_conversation(
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing conversation

    - **conversation_id**: The ID of the conversation to update
    - **message**: New message (optional)
    - **bot_reply**: New bot reply (optional)
    """
    conversation = crud.update_conversation(
        db,
        conversation_id=conversation_id,
        conversation_update=conversation_update
    )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return conversation


@app.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Delete a conversation

    - **conversation_id**: The ID of the conversation to delete
    """
    deleted = crud.delete_conversation(db, conversation_id=conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    return None  # 204 No Content


# ========== CHATBOT ENDPOINT (Enhanced with Database) ==========

# Pydantic models for chatbot (simpler than full conversation model)
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_message: str
    user_id: int  # Now requires user_id to link to database


class ChatResponse(BaseModel):
    bot_reply: str
    user_message: str
    conversation_id: int  # Return the saved conversation ID
    timestamp: str


# Simple chatbot logic function (from previous sessions)
def chatbot_reply(user_input: str) -> str:
    """Rule-based chatbot that matches patterns and returns responses"""
    message = user_input.lower().strip()

    if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
        return "Hi there! How can I help you today?"

    if "your name" in message or "who are you" in message:
        return "I'm FastAPI Bot, your friendly assistant built with FastAPI!"

    if "fastapi" in message:
        return "FastAPI is a modern, fast Python web framework for building APIs. It's awesome!"

    if "how are you" in message:
        return "I'm doing great! Thanks for asking. How can I assist you?"

    if "help" in message:
        return "I can chat with you! Try asking me about FastAPI, say hello, or ask my name!"

    return "Interesting! I'm still learning. Can you try asking something else?"


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chatbot endpoint - now saves to database!

    - **user_message**: The message from the user
    - **user_id**: The ID of the user sending the message
    """
    # Verify user exists
    user = crud.get_user(db, user_id=request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {request.user_id} not found"
        )

    # Get bot's reply
    bot_response = chatbot_reply(request.user_message)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save conversation to database
    conversation_data = schemas.ConversationCreate(
        user_id=request.user_id,
        message=request.user_message,
        bot_reply=bot_response
    )
    saved_conversation = crud.create_conversation(db, conversation_data)

    # Return response
    return ChatResponse(
        bot_reply=bot_response,
        user_message=request.user_message,
        conversation_id=saved_conversation.id,
        timestamp=timestamp
    )


# ========== UTILITY ENDPOINTS ==========

@app.get("/users/{user_id}/conversation-count")
def get_user_conversation_count(user_id: int, db: Session = Depends(get_db)):
    """Get count of conversations for a user"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    count = crud.count_user_conversations(db, user_id=user_id)
    return {"user_id": user_id, "conversation_count": count}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}


# ========== MONGODB ENDPOINTS ==========

@app.post("/mongo/users", response_model=mongo_models.User, status_code=status.HTTP_201_CREATED)
async def create_mongo_user(user: mongo_models.UserCreate, db=Depends(get_database)):
    """Create a new user in MongoDB"""
    # Check if email already exists
    existing_user = await mongo_crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await mongo_crud.create_user(db, user)


@app.get("/mongo/users", response_model=List[mongo_models.User])
async def get_mongo_users(skip: int = 0, limit: int = 100, db=Depends(get_database)):
    """Get list of users from MongoDB with pagination"""
    return await mongo_crud.get_users(db, skip=skip, limit=limit)


@app.get("/mongo/users/{user_id}", response_model=mongo_models.User)
async def get_mongo_user(user_id: str, db=Depends(get_database)):
    """Get a specific user from MongoDB by ID"""
    user = await mongo_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/mongo/conversations", response_model=mongo_models.Conversation, status_code=status.HTTP_201_CREATED)
async def create_mongo_conversation(conversation: mongo_models.ConversationCreate, db=Depends(get_database)):
    """Create a new conversation in MongoDB"""
    return await mongo_crud.create_conversation(db, conversation)


@app.get("/mongo/users/{user_id}/conversations", response_model=List[mongo_models.Conversation])
async def get_mongo_user_conversations(user_id: str, skip: int = 0, limit: int = 100, db=Depends(get_database)):
    """Get all conversations for a specific user from MongoDB"""
    return await mongo_crud.get_user_conversations(db, user_id, skip=skip, limit=limit)
