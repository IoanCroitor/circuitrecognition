from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import asc_parsing, circuit_recognition, health
from app.core.config import settings
from app.core.logging import setup_logging

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for circuit recognition and ASC file parsing",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Setup logging
setup_logging()

# Add CORS middleware if needed
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(asc_parsing.router, prefix=settings.API_V1_STR)
app.include_router(circuit_recognition.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Circuit Recognition API"}