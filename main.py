# Import the FastAPI class from fastapi library
from fastapi import FastAPI

# Create an instance of FastAPI application
app = FastAPI()

# Route decorator: handles GET requests at root endpoint "/"
@app.get("/")
def read_root():
    # FastAPI auto-converts Python dict to JSON response
    return {"message": "Hello World"}
