# Database connection configuration for SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL format: dialect+driver://username:password@host:port/database
# mysql+pymysql: MySQL database using PyMySQL driver
# root:root: username and password (change in production!)
# localhost:3306: host and port (MySQL default port)
# chatbot_db: database name we created
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/chatbot_db"

# Create database engine
# engine: Manages connections to the database
# echo=True: Prints all SQL queries (useful for learning/debugging)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Set to False in production for performance
)

# Create SessionLocal class
# SessionLocal: Factory for creating database sessions
# A session represents a "conversation" with the database
# autocommit=False: We manually control when to save changes
# autoflush=False: We manually control when to send changes to DB
# bind=engine: Tie this session to our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class
# Base: All our ORM models will inherit from this   MODEL=TABLE=SCHEMA
# This is the foundation for all our database tables
Base = declarative_base()

# Dependency function for FastAPI
# This function will be used in FastAPI endpoints to get a database session
# It creates a session, yields it to the endpoint, then closes it
def get_db():
    """
    Database session dependency for FastAPI endpoints.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            # db is automatically created and closed
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()  # Create new session
    try:
        yield db  # Provide session to the endpoint
    finally:
        db.close()  # Always close session, even if error occurs
