"""
Main application file for the FastAPI service.

This module initializes the FastAPI application, configures logging,
and includes the necessary routers and middleware.
"""
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from src.adapters.api.v1.customers.router import router as customers_router
from src.adapters.api.v1.health_check.router import (
    router as health_check_router,
)
from src.config.logging import configure_logging

# Configure logging before initializing the application
configure_logging()

app = FastAPI(
    title="Customer Service API",
    description="API for managing customers.",
    version="1.0.0",
)
"""The main FastAPI application instance."""

app.include_router(health_check_router, prefix="/health", tags=["Health"])
app.include_router(customers_router, prefix="/api/v1", tags=["Customers"])

app.add_middleware(CorrelationIdMiddleware)
