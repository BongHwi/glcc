from fastapi import FastAPI

app = FastAPI(
    title="GLCC - Global Logistics Command Center",
    description="Self-hosted platform for tracking deliveries worldwide",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GLCC - Global Logistics Command Center",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
