"""FastAPI application entry point."""

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.comments import router as comments_router
from app.api.v1.content import router as content_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.leads import router as leads_router
from app.api.v1.platforms import router as platforms_router
from app.api.v1.posts import router as posts_router
from app.api.v1.schedules import router as schedules_router
from app.config import settings
from app.database import get_db
from app.utils.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="AI Social Media Manager",
    description="AI-powered social media management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(leads_router, prefix="/api/v1")
app.include_router(platforms_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {"status": "healthy", "version": "1.0.0"}
