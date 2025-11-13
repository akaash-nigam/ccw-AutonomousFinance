"""Main FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from src.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize RabbitMQ connection
    # TODO: Load AI models/agents

    yield

    # Shutdown
    logger.info("shutting_down_application")
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Close RabbitMQ connections


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-native financial back-office platform with autonomous P2P, O2C, and R2R",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check() -> JSONResponse:
    """Basic health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }
    )


@app.get("/health/ready", tags=["health"])
async def readiness_check() -> JSONResponse:
    """Readiness check for Kubernetes."""
    # TODO: Check database connection
    # TODO: Check Redis connection
    # TODO: Check RabbitMQ connection
    return JSONResponse(
        content={
            "status": "ready",
            "checks": {
                "database": "ok",
                "redis": "ok",
                "rabbitmq": "ok",
            },
        }
    )


@app.get("/health/live", tags=["health"])
async def liveness_check() -> JSONResponse:
    """Liveness check for Kubernetes."""
    return JSONResponse(content={"status": "alive"})


# API v1 routes
# TODO: Include routers for invoice, payment, reconcile, journal, close, audit

# Root endpoint
@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """Root endpoint with API information."""
    return JSONResponse(
        content={
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "docs": f"{settings.api_v1_prefix}/docs",
            "health": "/health",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
    )
