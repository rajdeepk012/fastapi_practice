# Import the FastAPI class from fastapi library
from fastapi import FastAPI

# Create an instance of FastAPI application
app = FastAPI()

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}

# Path parameter: {user_id} is a dynamic variable in the URL
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # user_id is extracted from URL and validated as integer
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
