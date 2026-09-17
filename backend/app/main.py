from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Enterprise Multi-Agent Business Intelligence Platform (EMBIP) Backend API",
    version="0.1.0",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=200, tags=["Health"])
async def health_check():
    """Real health check endpoint returning status ok."""
    return {"status": "ok"}


@app.get("/", status_code=200, tags=["Root"])
async def root():
    """Root metadata endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "status": "running",
        "phase": "Phase 1 - Project Foundation",
    }
