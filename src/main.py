from fastapi import FastAPI
from src.adapters.api.v1.customers.router import router as customers_router
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}



app.include_router(customers_router)

app.add_middleware(CorrelationIdMiddleware)
