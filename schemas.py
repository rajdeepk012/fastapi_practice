# Pydantic schemas for API request/response validation and serialization
# These are DIFFERENT from SQLAlchemy models!
#
# SQLAlchemy models (models.py) = Database structure (ORM)
# Pydantic schemas (schemas.py) = API validation and serialization
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ========== USER SCHEMAS ==========

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    username: str
    email: EmailStr  # Validates email format


class UserCreate(UserBase):
    """Schema for creating a new user (API request)"""
    # Inherits username and email from UserBase
    # Add any additional fields needed only for creation
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user (API request)"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    # All fields optional - can update just username, just email, or both


class User(UserBase):
    """
    Schema for user response (API response)
    This is what the API returns to clients
    """
    id: int
    created_at: datetime

    class Config:
        # This allows Pydantic to work with SQLAlchemy models
        # Enables: User.from_orm(db_user)
        from_attributes = True  # Pydantic v2 (was orm_mode = True in v1)


class UserWithConversations(User):
    """User schema with related conversations included"""
    conversations: List['Conversation'] = []
    # List of Conversation objects (defined below)


# ========== CONVERSATION SCHEMAS ==========

class ConversationBase(BaseModel):
    """Base conversation schema"""
    message: str
    bot_reply: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation (API request)"""
    user_id: int
    # Must specify which user this conversation belongs to


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation (API request)"""
    message: Optional[str] = None
    bot_reply: Optional[str] = None
    # Both fields optional


class Conversation(ConversationBase):
    """
    Schema for conversation response (API response)
    """
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationWithUser(Conversation):
    """Conversation schema with user details included"""
    user: User
    # Nested User object


# Update forward references for type hints
# This is needed because UserWithConversations references Conversation
# before Conversation is fully defined
UserWithConversations.model_rebuild()
