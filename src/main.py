from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from src.adapters.api.v1.customers.router import router as customers_router
from src.config.logging import configure_logging

configure_logging()
app = FastAPI()


app.include_router(customers_router)

app.add_middleware(CorrelationIdMiddleware)
