from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.rate_limit import _rate_limit_exceeded_handler, limiter

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Enterprise Multi-Agent Business Intelligence Platform (EMBIP) Backend API",
    version="0.1.0",
)

# Register slowapi Limiter on app state & Exception Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", status_code=200, tags=["Health"])
@limiter.limit(lambda: f"{settings.RATE_LIMIT_HEALTH_PER_MINUTE}/minute")
async def health_check(request: Request):
    """Real health check endpoint returning status ok."""
    return {"status": "ok"}


@app.get("/", status_code=200, tags=["Root"])
@limiter.limit(lambda: f"{settings.RATE_LIMIT_HEALTH_PER_MINUTE}/minute")
async def root(request: Request):
    """Root metadata endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "status": "running",
        "phase": "Phase 3 - Authentication & Authorization",
    }
