"""
API Router for Customer Management.

This module defines the FastAPI router for handling customer-related
endpoints, such as creating, retrieving, and updating customers.
"""
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.di.v1.get_create_customer_uc import get_initiate_customer_creation_uc
from src.domain.exceptions import CustomerAlreadyExistsError
from src.usecases.v1.customers.create_customer import InitiateCustomerCreation
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead

router = APIRouter()


@router.post(
    "/",
    summary="Initiate asynchronous customer creation",
    status_code=202,
    response_model=CustomerRead,
)
async def create_customer(
    payload: CustomerCreate,
    controller: InitiateCustomerCreation = Depends(
        get_initiate_customer_creation_uc
    ),
) -> CustomerRead:
    """
    Asynchronously initiates the customer creation process.

    This endpoint receives customer data, performs initial validation,
    generates a unique ID, and publishes a creation event. The actual
    customer creation is handled by a background worker.

    Args:
        payload: The customer data to be created, following the
            `CustomerCreate` schema.
        controller: The use case controller, injected as a dependency,
            responsible for orchestrating the creation process.

    Returns:
        The details of the customer being created, including the generated ID,
        confirming that the process has been initiated.

    Raises:
        HTTPException (409 Conflict): If a customer with the same email
            already exists.
        HTTPException (500 Internal Server Error): For any other unexpected
            errors during the initiation process.
    """
    try:
        return await controller.execute(payload)
    except CustomerAlreadyExistsError as e:
        logger.warning(f"Business rule violation: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.exception(f"Unhandled error initiating customer creation: {e}")
        raise HTTPException(
            status_code=500, detail="An internal error occurred."
        )
