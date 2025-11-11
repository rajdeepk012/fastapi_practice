# Test script for CRUD operations
from database import SessionLocal
import crud
import schemas

print("=" * 60)
print("Testing CRUD Operations")
print("=" * 60)

# Create database session
db = SessionLocal()

try:
    # ========== TEST 1: Get all users ==========
    print("\n1. Getting all users...")
    print("-" * 60)
    users = crud.get_users(db, skip=0, limit=10)
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  - {user.username} ({user.email})")

    # ========== TEST 2: Get specific user ==========
    print("\n2. Getting user with id=1...")
    print("-" * 60)
    user = crud.get_user(db, user_id=1)
    if user:
        print(f"Found: {user.username} ({user.email})")
    else:
        print("User not found!")

    # ========== TEST 3: Get user by email ==========
    print("\n3. Getting user by email...")
    print("-" * 60)
    user = crud.get_user_by_email(db, email="ram@god.com")
    if user:
        print(f"Found: {user.username} (ID: {user.id})")
    else:
        print("User not found!")

    # ========== TEST 4: Count user's conversations ==========
    print("\n4. Counting conversations for user id=1...")
    print("-" * 60)
    count = crud.count_user_conversations(db, user_id=1)
    print(f"User has {count} conversations")

    # ========== TEST 5: Get user's conversations ==========
    print("\n5. Getting conversations for user id=1...")
    print("-" * 60)
    conversations = crud.get_user_conversations(db, user_id=1)
    print(f"Found {len(conversations)} conversations:")
    for conv in conversations:
        print(f"  - {conv.message[:30]}... → {conv.bot_reply[:30]}...")

    # ========== TEST 6: Get user with conversations (JOIN) ==========
    print("\n6. Getting user WITH conversations (using JOIN)...")
    print("-" * 60)
    user = crud.get_user_with_conversations(db, user_id=1)
    if user:
        print(f"User: {user.username}")
        print(f"Conversations loaded: {len(user.conversations)}")
        for conv in user.conversations:
            print(f"  - {conv.message}")

    # ========== TEST 7: Create new conversation ==========
    print("\n7. Creating new conversation...")
    print("-" * 60)
    new_conv_data = schemas.ConversationCreate(
        user_id=1,
        message="This is a test message from CRUD!",
        bot_reply="This is a test reply from CRUD!"
    )
    new_conv = crud.create_conversation(db, new_conv_data)
    print(f"Created conversation with ID: {new_conv.id}")
    print(f"Message: {new_conv.message}")
    print(f"Reply: {new_conv.bot_reply}")

    # ========== TEST 8: Update conversation ==========
    print("\n8. Updating conversation...")
    print("-" * 60)
    update_data = schemas.ConversationUpdate(
        bot_reply="Updated reply from CRUD test!"
    )
    updated_conv = crud.update_conversation(db, new_conv.id, update_data)
    if updated_conv:
        print(f"Updated conversation ID {updated_conv.id}")
        print(f"New reply: {updated_conv.bot_reply}")

    # ========== TEST 9: Delete conversation ==========
    print("\n9. Deleting test conversation...")
    print("-" * 60)
    deleted = crud.delete_conversation(db, new_conv.id)
    if deleted:
        print(f"✅ Successfully deleted conversation ID {new_conv.id}")
    else:
        print("❌ Failed to delete conversation")

    # ========== TEST 10: Pagination example ==========
    print("\n10. Testing pagination...")
    print("-" * 60)
    print("Page 1 (first 2 users):")
    page1 = crud.get_users(db, skip=0, limit=2)
    for user in page1:
        print(f"  - {user.username}")

    print("\nPage 2 (next 2 users):")
    page2 = crud.get_users(db, skip=2, limit=2)
    for user in page2:
        print(f"  - {user.username}")

    print("\n" + "=" * 60)
    print("✅ All CRUD tests passed!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
    print("\n🔒 Database session closed.")
