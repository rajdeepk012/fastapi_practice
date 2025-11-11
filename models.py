# SQLAlchemy ORM Models - Python classes that map to MySQL tables
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# User Model - Maps to 'users' table in MySQL
class User(Base):
    """
    User model representing the users table.

    Table: users
    Columns: id, username, email, created_at
    """
    # Tell SQLAlchemy which table this class maps to
    __tablename__ = "users"

    # Define columns - each Column maps to a column in the MySQL table
    # Column(Type, constraints...)
    id = Column(Integer, primary_key=True, index=True)
    # Integer: INT in MySQL
    # primary_key=True: This is the PRIMARY KEY
    # index=True: Create an index for faster lookups

    username = Column(String(50), nullable=False)
    # String(50): VARCHAR(50) in MySQL
    # nullable=False: NOT NULL constraint

    email = Column(String(100), unique=True, nullable=False)
    # unique=True: UNIQUE constraint
    # nullable=False: NOT NULL constraint

    created_at = Column(DateTime, server_default=func.now())
    # DateTime: DATETIME in MySQL
    # server_default=func.now(): DEFAULT CURRENT_TIMESTAMP

    # Relationship: One user has many conversations
    # This is NOT a column in the database!
    # It's a Python convenience to access related conversations
    conversations = relationship("Conversation", back_populates="user")
    # "Conversation": Related model name (as string)
    # back_populates="user": Links to 'user' attribute in Conversation model


# Conversation Model - Maps to 'conversations' table in MySQL
class Conversation(Base):
    """
    Conversation model representing the conversations table.

    Table: conversations
    Columns: id, user_id, message, bot_reply, created_at
    Relationship: Many conversations belong to one user
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ForeignKey("users.id"): References users.id column
    # This creates the FOREIGN KEY constraint in MySQL

    message = Column(Text, nullable=False)
    # Text: TEXT in MySQL (for long strings)

    bot_reply = Column(Text, nullable=True)
    # nullable=True: Can be NULL (optional)

    created_at = Column(DateTime, server_default=func.now())

    # Relationship: Each conversation belongs to one user
    # This is NOT a column! It's a Python convenience
    user = relationship("User", back_populates="conversations")
    # back_populates="conversations": Links to 'conversations' in User model
    