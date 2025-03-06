from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """Test endpoint to check if the server is running."""
    return {"message": "Server is running"}
