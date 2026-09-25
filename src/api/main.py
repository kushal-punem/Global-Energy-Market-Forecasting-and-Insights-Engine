from fastapi import FastAPI

app = FastAPI(
    title="Global Energy Market Engine",
    description="API for WTI crude oil market data and analytics",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Global Energy Market Engine API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }