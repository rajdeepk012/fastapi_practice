# Test script to verify SQLAlchemy models work with MySQL database
from database import SessionLocal, engine
from models import User, Conversation

print("=" * 60)
print("Testing SQLAlchemy ORM Connection to MySQL")
print("=" * 60)

# Create a database session
# This is the "conversation" with the database
db = SessionLocal()

try:
    print("\n1. Querying all users from database...")
    print("-" * 60)

    # ORM Query: Python code that gets translated to SQL
    users = db.query(User).all()
    # Behind the scenes: SELECT * FROM users;

    print(f"Found {len(users)} users:")
    for user in users:
        # Accessing data using dot notation (ORM mapping!)
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")

    print("\n2. Getting a specific user (id=1)...")
    print("-" * 60)

    # ORM Query with filter
    user = db.query(User).filter(User.id == 1).first()
    # Behind the scenes: SELECT * FROM users WHERE id = 1 LIMIT 1;

    if user:
        print(f"User found: {user.username} ({user.email})")
        print(f"Created at: {user.created_at}")
    else:
        print("User not found!")

    print("\n3. Getting conversations...")
    print("-" * 60)

    # ORM Query for conversations
    conversations = db.query(Conversation).all()
    # Behind the scenes: SELECT * FROM conversations;

    print(f"Found {len(conversations)} conversations:")
    for conv in conversations:
        print(f"  - ID: {conv.id}")
        print(f"    User ID: {conv.user_id}")
        print(f"    Message: {conv.message}")
        print(f"    Bot Reply: {conv.bot_reply}")
        print()

    print("\n4. Using relationship (JOIN demo)...")
    print("-" * 60)

    # Get user with id=1
    user = db.query(User).filter(User.id == 1).first()

    if user:
        print(f"User: {user.username}")
        print(f"Their conversations:")

        # Access related conversations through relationship!
        # This is the power of ORM - no manual JOIN needed!
        for conv in user.conversations:
            # Behind the scenes: SELECT * FROM conversations WHERE user_id = 1;
            print(f"  - {conv.message} → {conv.bot_reply}")

    print("\n5. Reverse relationship (Conversation → User)...")
    print("-" * 60)

    # Get first conversation
    conversation = db.query(Conversation).first()

    if conversation:
        print(f"Message: {conversation.message}")
        print(f"Bot Reply: {conversation.bot_reply}")

        # Access user through relationship!
        print(f"Sent by: {conversation.user.username} ({conversation.user.email})")
        # Behind the scenes: SELECT * FROM users WHERE id = <user_id>;

    print("\n" + "=" * 60)
    print("✅ All tests passed! ORM is working correctly!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

finally:
    # Always close the session
    db.close()
    print("\n🔒 Database session closed.")
