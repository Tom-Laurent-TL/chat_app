from fastapi import FastAPI
from app.router import router

app = FastAPI(title="🐙 Octopus App")

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include all feature routers (automatically mounted)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
