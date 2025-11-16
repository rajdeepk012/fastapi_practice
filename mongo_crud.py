# MongoDB CRUD Operations
# All functions are ASYNC (use await) for non-blocking operations

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

import mongo_models


# ============================================================================
# USER CRUD OPERATIONS
# ============================================================================

async def create_user(db: AsyncIOMotorDatabase, user: mongo_models.UserCreate) -> mongo_models.UserInDB:
    """
    Create a new user in MongoDB.

    Args:
        db: MongoDB database instance
        user: User data from client (UserCreate model)

    Returns:
        Created user with _id and created_at

    Example:
        user_data = UserCreate(username="alice", email="alice@example.com")
        new_user = await create_user(db, user_data)
    """
    # Convert Pydantic model to dictionary
    user_dict = user.dict()

    # Add created_at timestamp
    user_dict["created_at"] = datetime.utcnow()

    # Insert into MongoDB
    # insert_one() returns InsertOneResult with inserted_id
    result = await db.users.insert_one(user_dict)

    # Get the inserted document
    created_user = await db.users.find_one({"_id": result.inserted_id})

    # Return as UserInDB model
    return mongo_models.UserInDB(**created_user)


async def get_user(db: AsyncIOMotorDatabase, user_id: str) -> Optional[mongo_models.UserInDB]:
    """
    Get a single user by ID.

    Args:
        db: MongoDB database instance
        user_id: User's ObjectId as string

    Returns:
        User document or None if not found

    Example:
        user = await get_user(db, "507f1f77bcf86cd799439011")
    """
    # MongoDB requires ObjectId, not string
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if user:
        return mongo_models.UserInDB(**user)
    return None


async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[mongo_models.UserInDB]:
    """
    Get a user by username.

    Args:
        db: MongoDB database instance
        username: User's username

    Returns:
        User document or None if not found

    Example:
        user = await get_user_by_username(db, "alice")
    """
    user = await db.users.find_one({"username": username})

    if user:
        return mongo_models.UserInDB(**user)
    return None


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[mongo_models.UserInDB]:
    """
    Get a user by email.

    Args:
        db: MongoDB database instance
        email: User's email address

    Returns:
        User document or None if not found

    Example:
        user = await get_user_by_email(db, "alice@example.com")
    """
    user = await db.users.find_one({"email": email})

    if user:
        return mongo_models.UserInDB(**user)
    return None


async def get_users(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[mongo_models.UserInDB]:
    """
    Get list of users with pagination.

    Args:
        db: MongoDB database instance
        skip: Number of documents to skip (default: 0)
        limit: Maximum number of documents to return (default: 100)

    Returns:
        List of user documents

    Example:
        users = await get_users(db, skip=0, limit=10)  # First 10 users
        users = await get_users(db, skip=10, limit=10) # Next 10 users
    """
    # find() returns a cursor (not the actual documents!)
    # Must use to_list() to get actual documents
    cursor = db.users.find().skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)

    # Convert each document to UserInDB model
    return [mongo_models.UserInDB(**user) for user in users]


async def update_user(
    db: AsyncIOMotorDatabase,
    user_id: str,
    user_update: mongo_models.UserUpdate
) -> Optional[mongo_models.UserInDB]:
    """
    Update a user document.

    Args:
        db: MongoDB database instance
        user_id: User's ObjectId as string
        user_update: Fields to update (UserUpdate model)

    Returns:
        Updated user document or None if not found

    Example:
        update_data = UserUpdate(username="alice_new")
        updated_user = await update_user(db, "507f...", update_data)
    """
    # Only update fields that were provided (exclude_unset=True)
    update_data = user_update.dict(exclude_unset=True)

    if not update_data:
        # No fields to update
        return await get_user(db, user_id)

    # Update the document
    # $set operator updates specified fields
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        # No document was modified (might not exist)
        return None

    # Return updated document
    return await get_user(db, user_id)


async def delete_user(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """
    Delete a user document.

    Args:
        db: MongoDB database instance
        user_id: User's ObjectId as string

    Returns:
        True if deleted, False if not found

    Example:
        deleted = await delete_user(db, "507f1f77bcf86cd799439011")
        if deleted:
            print("User deleted!")
    """
    result = await db.users.delete_one({"_id": ObjectId(user_id)})

    # deleted_count = number of documents deleted (0 or 1)
    return result.deleted_count > 0


# ============================================================================
# CONVERSATION CRUD OPERATIONS
# ============================================================================

async def create_conversation(
    db: AsyncIOMotorDatabase,
    conversation: mongo_models.ConversationCreate
) -> mongo_models.ConversationInDB:
    """
    Create a new conversation in MongoDB.

    Args:
        db: MongoDB database instance
        conversation: Conversation data (ConversationCreate model)

    Returns:
        Created conversation with _id and created_at

    Example:
        conv_data = ConversationCreate(
            user_id="alice",
            message="Hello",
            bot_reply="Hi there!"
        )
        new_conv = await create_conversation(db, conv_data)
    """
    conv_dict = conversation.dict()
    conv_dict["created_at"] = datetime.utcnow()

    result = await db.conversations.insert_one(conv_dict)
    created_conv = await db.conversations.find_one({"_id": result.inserted_id})

    return mongo_models.ConversationInDB(**created_conv)


async def get_conversation(
    db: AsyncIOMotorDatabase,
    conversation_id: str
) -> Optional[mongo_models.ConversationInDB]:
    """
    Get a single conversation by ID.

    Args:
        db: MongoDB database instance
        conversation_id: Conversation's ObjectId as string

    Returns:
        Conversation document or None if not found
    """
    conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})

    if conv:
        return mongo_models.ConversationInDB(**conv)
    return None


async def get_conversations(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 100
) -> List[mongo_models.ConversationInDB]:
    """
    Get list of conversations with pagination.

    Args:
        db: MongoDB database instance
        skip: Number of documents to skip
        limit: Maximum number of documents to return

    Returns:
        List of conversation documents
    """
    cursor = db.conversations.find().skip(skip).limit(limit)
    conversations = await cursor.to_list(length=limit)

    return [mongo_models.ConversationInDB(**conv) for conv in conversations]


async def get_user_conversations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[mongo_models.ConversationInDB]:
    """
    Get all conversations for a specific user.

    Args:
        db: MongoDB database instance
        user_id: Username to filter by
        skip: Number of documents to skip
        limit: Maximum number of documents to return

    Returns:
        List of conversation documents for this user

    Example:
        alice_convos = await get_user_conversations(db, "alice")
    """
    # Filter by user_id field
    cursor = db.conversations.find({"user_id": user_id}).skip(skip).limit(limit)
    conversations = await cursor.to_list(length=limit)

    return [mongo_models.ConversationInDB(**conv) for conv in conversations]


async def count_user_conversations(db: AsyncIOMotorDatabase, user_id: str) -> int:
    """
    Count total conversations for a user.

    Args:
        db: MongoDB database instance
        user_id: Username to count for

    Returns:
        Number of conversations

    Example:
        count = await count_user_conversations(db, "alice")
        print(f"Alice has {count} conversations")
    """
    count = await db.conversations.count_documents({"user_id": user_id})
    return count


async def update_conversation(
    db: AsyncIOMotorDatabase,
    conversation_id: str,
    conversation_update: mongo_models.ConversationUpdate
) -> Optional[mongo_models.ConversationInDB]:
    """
    Update a conversation document.

    Args:
        db: MongoDB database instance
        conversation_id: Conversation's ObjectId as string
        conversation_update: Fields to update

    Returns:
        Updated conversation or None if not found
    """
    update_data = conversation_update.dict(exclude_unset=True)

    if not update_data:
        return await get_conversation(db, conversation_id)

    result = await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return None

    return await get_conversation(db, conversation_id)


async def delete_conversation(db: AsyncIOMotorDatabase, conversation_id: str) -> bool:
    """
    Delete a conversation document.

    Args:
        db: MongoDB database instance
        conversation_id: Conversation's ObjectId as string

    Returns:
        True if deleted, False if not found
    """
    result = await db.conversations.delete_one({"_id": ObjectId(conversation_id)})
    return result.deleted_count > 0
