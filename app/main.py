"""
QuensultingAI Dental Clinic — AI Voice Agent
FastAPI application entrypoint.

Registers all API routes, configures CORS, and sets up
the application lifespan for startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import logger
from app.api import webhook, booking, availability, faq, transfer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Runs startup tasks before the app begins serving requests,
    and cleanup tasks when the app shuts down.
    """
    # --- Startup ---
    logger.info("=" * 60)
    logger.info(f"  {settings.clinic_name} — Voice Agent")
    logger.info(f"  Environment: {settings.app_env}")
    logger.info(f"  Listening on: {settings.app_host}:{settings.app_port}")
    logger.info("=" * 60)
    logger.info("Application startup complete")

    yield  # App is running

    # --- Shutdown ---
    logger.info("Application shutting down")


# ================================================================
# Create FastAPI application
# ================================================================
app = FastAPI(
    title="QuensultingAI Dental Voice Agent",
    description=(
        "AI-powered voice receptionist for QuensultingAI Dental Clinic. "
        "Handles inbound calls, books appointments, answers FAQs, "
        "and transfers to human agents when needed."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    lifespan=lifespan,
)

# ================================================================
# CORS Middleware
# ================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# Register API Routes
# ================================================================
app.include_router(webhook.router, tags=["Webhooks"])
app.include_router(booking.router, tags=["Appointments"])
app.include_router(availability.router, tags=["Appointments"])
app.include_router(faq.router, tags=["FAQ"])
app.include_router(transfer.router, tags=["Transfer"])


# ================================================================
# Health Check
# ================================================================
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        {"status": "healthy", "service": "...", "version": "..."}
    """
    return {
        "status": "healthy",
        "service": "QuensultingAI Voice Agent",
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "message": f"Welcome to {settings.clinic_name} Voice Agent API",
        "docs": "/docs",
        "health": "/health",
    }
