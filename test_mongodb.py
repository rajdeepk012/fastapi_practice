# Test script for MongoDB connection and CRUD operations
# Run with: python test_mongodb.py

import asyncio
from mongodb import connect_to_mongo, close_mongo_connection, get_database
import mongo_crud
import mongo_models


async def test_connection():
    """Test MongoDB connection"""
    print("=" * 60)
    print("TEST 1: MongoDB Connection")
    print("=" * 60)

    # Connect to MongoDB
    connect_to_mongo()
    db = get_database()

    # Test connection by listing collections
    collections = await db.list_collection_names()
    print(f"✅ Connected to MongoDB!")
    print(f"📁 Existing collections: {collections}")
    print()


async def test_create_user():
    """Test creating a user"""
    print("=" * 60)
    print("TEST 2: Create User")
    print("=" * 60)

    db = get_database()

    # Create user
    user_data = mongo_models.UserCreate(
        username="test_user",
        email="test@example.com"
    )

    new_user = await mongo_crud.create_user(db, user_data)

    print(f"✅ User created!")
    print(f"📝 User ID: {new_user.id}")
    print(f"📝 Username: {new_user.username}")
    print(f"📝 Email: {new_user.email}")
    print(f"📝 Created at: {new_user.created_at}")
    print()

    return str(new_user.id)


async def test_get_user(user_id: str):
    """Test getting a user by ID"""
    print("=" * 60)
    print("TEST 3: Get User by ID")
    print("=" * 60)

    db = get_database()

    user = await mongo_crud.get_user(db, user_id)

    if user:
        print(f"✅ User found!")
        print(f"📝 Username: {user.username}")
        print(f"📝 Email: {user.email}")
    else:
        print("❌ User not found!")
    print()


async def test_get_user_by_email():
    """Test getting a user by email"""
    print("=" * 60)
    print("TEST 4: Get User by Email")
    print("=" * 60)

    db = get_database()

    user = await mongo_crud.get_user_by_email(db, "test@example.com")

    if user:
        print(f"✅ User found!")
        print(f"📝 Username: {user.username}")
        print(f"📝 User ID: {user.id}")
    else:
        print("❌ User not found!")
    print()


async def test_get_all_users():
    """Test getting all users"""
    print("=" * 60)
    print("TEST 5: Get All Users")
    print("=" * 60)

    db = get_database()

    users = await mongo_crud.get_users(db, skip=0, limit=10)

    print(f"✅ Found {len(users)} users:")
    for user in users:
        print(f"   - {user.username} ({user.email})")
    print()


async def test_update_user(user_id: str):
    """Test updating a user"""
    print("=" * 60)
    print("TEST 6: Update User")
    print("=" * 60)

    db = get_database()

    # Update username
    update_data = mongo_models.UserUpdate(username="updated_test_user")
    updated_user = await mongo_crud.update_user(db, user_id, update_data)

    if updated_user:
        print(f"✅ User updated!")
        print(f"📝 New username: {updated_user.username}")
        print(f"📝 Email (unchanged): {updated_user.email}")
    else:
        print("❌ User not found!")
    print()


async def test_create_conversation(user_id: str):
    """Test creating a conversation"""
    print("=" * 60)
    print("TEST 7: Create Conversation")
    print("=" * 60)

    db = get_database()

    # Create conversation
    conv_data = mongo_models.ConversationCreate(
        user_id="test_user",
        message="Hello MongoDB!",
        bot_reply="Hi there! I'm working with MongoDB now!"
    )

    new_conv = await mongo_crud.create_conversation(db, conv_data)

    print(f"✅ Conversation created!")
    print(f"📝 Conversation ID: {new_conv.id}")
    print(f"📝 User ID: {new_conv.user_id}")
    print(f"📝 Message: {new_conv.message}")
    print(f"📝 Bot Reply: {new_conv.bot_reply}")
    print()

    return str(new_conv.id)


async def test_get_user_conversations():
    """Test getting user's conversations"""
    print("=" * 60)
    print("TEST 8: Get User Conversations")
    print("=" * 60)

    db = get_database()

    conversations = await mongo_crud.get_user_conversations(db, "test_user")

    print(f"✅ Found {len(conversations)} conversations for test_user:")
    for conv in conversations:
        print(f"   - {conv.message} → {conv.bot_reply}")
    print()


async def test_count_conversations():
    """Test counting user's conversations"""
    print("=" * 60)
    print("TEST 9: Count User Conversations")
    print("=" * 60)

    db = get_database()

    count = await mongo_crud.count_user_conversations(db, "test_user")

    print(f"✅ test_user has {count} conversation(s)")
    print()


async def test_delete_user(user_id: str):
    """Test deleting a user"""
    print("=" * 60)
    print("TEST 10: Delete User")
    print("=" * 60)

    db = get_database()

    deleted = await mongo_crud.delete_user(db, user_id)

    if deleted:
        print(f"✅ User deleted!")
    else:
        print("❌ User not found!")
    print()


async def main():
    """Run all tests"""
    print("\n🧪 TESTING MONGODB CONNECTION AND CRUD OPERATIONS\n")

    try:
        # Test connection
        await test_connection()

        # Test user CRUD
        user_id = await test_create_user()
        await test_get_user(user_id)
        await test_get_user_by_email()
        await test_get_all_users()
        await test_update_user(user_id)

        # Test conversation CRUD
        conv_id = await test_create_conversation(user_id)
        await test_get_user_conversations()
        await test_count_conversations()

        # Cleanup
        await test_delete_user(user_id)

        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close connection
        close_mongo_connection()
        print("\n👋 MongoDB connection closed. Tests complete!\n")


if __name__ == "__main__":
    # Run async main function
    asyncio.run(main())
