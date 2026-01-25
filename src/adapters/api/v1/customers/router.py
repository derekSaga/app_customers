from fastapi import APIRouter, Depends, HTTPException

from src.di.v1.get_create_customer_uc import get_create_customer_use_case
from src.usecases.v1.customers.create_customer import CreateCustomer
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead
from loguru import logger


router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.post("/", summary="Create a new customer", status_code=201)
async def create_customer(
    payload: CustomerCreate,
    controller: CreateCustomer = Depends(get_create_customer_use_case),
) -> CustomerRead:
    """
    Create a new customer.
    """
    try:
        return await controller.execute(payload)
    except Exception as e:
        logger.exception(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
