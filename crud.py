# CRUD operations (Create, Read, Update, Delete)
# These functions handle all database operations
# Endpoints call these functions instead of writing SQLAlchemy queries directly
from sqlalchemy.orm import Session
from typing import Optional, List
import models
import schemas


# ========== USER CRUD OPERATIONS ==========

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Get a single user by ID

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        User object or None if not found

    SQL Generated:
        SELECT * FROM users WHERE id = {user_id} LIMIT 1;
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get a user by email address
    Useful for checking if email already exists

    SQL Generated:
        SELECT * FROM users WHERE email = {email} LIMIT 1;
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get a list of users with pagination

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        List of User objects

    SQL Generated:
        SELECT * FROM users LIMIT {limit} OFFSET {skip};

    Example:
        get_users(db, skip=0, limit=10)   # First 10 users
        get_users(db, skip=10, limit=10)  # Next 10 users (11-20)
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user

    Args:
        db: Database session
        user: Pydantic schema with user data (username, email)

    Returns:
        Created User object with id and created_at from database

    SQL Generated:
        INSERT INTO users (username, email) VALUES ({username}, {email});
        SELECT * FROM users WHERE id = LAST_INSERT_ID();
    """
    # Create SQLAlchemy model from Pydantic schema
    db_user = models.User(
        username=user.username,
        email=user.email
    )

    db.add(db_user)  # Add to session
    db.commit()  # Save to database
    db.refresh(db_user)  # Refresh to get id and created_at from database

    return db_user


def update_user(
    db: Session,
    user_id: int,
    user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """
    Update an existing user

    Args:
        db: Database session
        user_id: ID of user to update
        user_update: Pydantic schema with fields to update

    Returns:
        Updated User object or None if not found

    SQL Generated:
        SELECT * FROM users WHERE id = {user_id};
        UPDATE users SET username={username}, email={email} WHERE id={user_id};
    """
    # Get existing user
    db_user = get_user(db, user_id)

    if not db_user:
        return None

    # Update only fields that were provided
    update_data = user_update.model_dump(exclude_unset=True)
    # exclude_unset=True means: only include fields that were actually set
    # Example: If user_update = {"username": "new_name"}, email is not updated

    for field, value in update_data.items():
        setattr(db_user, field, value)
        # setattr(obj, "username", "new_name") is same as obj.username = "new_name"

    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user

    Args:
        db: Database session
        user_id: ID of user to delete

    Returns:
        True if deleted, False if not found

    SQL Generated:
        SELECT * FROM users WHERE id = {user_id};
        DELETE FROM users WHERE id = {user_id};
    """
    db_user = get_user(db, user_id)

    if not db_user:
        return False

    db.delete(db_user)
    db.commit()

    return True


# ========== CONVERSATION CRUD OPERATIONS ==========

def get_conversation(db: Session, conversation_id: int) -> Optional[models.Conversation]:
    """
    Get a single conversation by ID

    SQL Generated:
        SELECT * FROM conversations WHERE id = {conversation_id} LIMIT 1;
    """
    return db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()


def get_conversations(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.Conversation]:
    """
    Get all conversations with pagination

    SQL Generated:
        SELECT * FROM conversations
        ORDER BY created_at DESC
        LIMIT {limit} OFFSET {skip};
    """
    return db.query(models.Conversation)\
        .order_by(models.Conversation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_user_conversations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Conversation]:
    """
    Get all conversations for a specific user

    Args:
        db: Database session
        user_id: User's ID
        skip: Pagination offset
        limit: Max results

    Returns:
        List of Conversation objects for this user

    SQL Generated:
        SELECT * FROM conversations
        WHERE user_id = {user_id}
        ORDER BY created_at DESC
        LIMIT {limit} OFFSET {skip};
    """
    return db.query(models.Conversation)\
        .filter(models.Conversation.user_id == user_id)\
        .order_by(models.Conversation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def create_conversation(
    db: Session,
    conversation: schemas.ConversationCreate
) -> models.Conversation:
    """
    Create a new conversation

    Args:
        db: Database session
        conversation: Pydantic schema with conversation data

    Returns:
        Created Conversation object

    SQL Generated:
        INSERT INTO conversations (user_id, message, bot_reply)
        VALUES ({user_id}, {message}, {bot_reply});
    """
    db_conversation = models.Conversation(
        user_id=conversation.user_id,
        message=conversation.message,
        bot_reply=conversation.bot_reply
    )

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


def update_conversation(
    db: Session,
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate
) -> Optional[models.Conversation]:
    """
    Update an existing conversation

    SQL Generated:
        SELECT * FROM conversations WHERE id = {conversation_id};
        UPDATE conversations SET ... WHERE id = {conversation_id};
    """
    db_conversation = get_conversation(db, conversation_id)

    if not db_conversation:
        return None

    # Update only provided fields
    update_data = conversation_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_conversation, field, value)

    db.commit()
    db.refresh(db_conversation)

    return db_conversation


def delete_conversation(db: Session, conversation_id: int) -> bool:
    """
    Delete a conversation

    Returns:
        True if deleted, False if not found

    SQL Generated:
        SELECT * FROM conversations WHERE id = {conversation_id};
        DELETE FROM conversations WHERE id = {conversation_id};
    """
    db_conversation = get_conversation(db, conversation_id)

    if not db_conversation:
        return False

    db.delete(db_conversation)
    db.commit()

    return True


# ========== ADVANCED QUERIES ==========

def get_user_with_conversations(db: Session, user_id: int) -> Optional[models.User]:
    """
    Get a user with all their conversations loaded
    Uses eager loading to fetch everything in one query

    SQL Generated (with JOIN):
        SELECT users.*, conversations.*
        FROM users
        LEFT JOIN conversations ON users.id = conversations.user_id
        WHERE users.id = {user_id};
    """
    from sqlalchemy.orm import joinedload

    return db.query(models.User)\
        .options(joinedload(models.User.conversations))\
        .filter(models.User.id == user_id)\
        .first()


def count_user_conversations(db: Session, user_id: int) -> int:
    """
    Count how many conversations a user has

    SQL Generated:
        SELECT COUNT(*) FROM conversations WHERE user_id = {user_id};
    """
    return db.query(models.Conversation)\
        .filter(models.Conversation.user_id == user_id)\
        .count()
