from fastapi import FastAPI
from tech_challenge_02 import main_router

app = FastAPI(
    title="Tech Challenge 02 API",
    description="API for Tech Challenge 02",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc"  # ReDoc endpoint
)

# Include routers
app.include_router(main_router)

def main():
    import uvicorn
    uvicorn.run(
        "tech_challenge_02.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main() 