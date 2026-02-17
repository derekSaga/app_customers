from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.di.v1.get_create_customer_uc import get_initiate_customer_creation_uc
from src.domain.exceptions import CustomerAlreadyExistsError
from src.usecases.v1.customers.create_customer import InitiateCustomerCreation
from src.usecases.v1.schemas.api.customer import CustomerCreate, CustomerRead

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.post("/", summary="Initiate customer creation", status_code=202)
async def create_customer(
    payload: CustomerCreate,
    controller: InitiateCustomerCreation = Depends(
        get_initiate_customer_creation_uc
    )
) -> CustomerRead:
    """
    Inicia o processo de criação de cliente de forma assíncrona.
    Valida as regras iniciais, gera o ID e publica o evento de criação.
    """
    try:
        return await controller.execute(payload)
    except CustomerAlreadyExistsError as e:
        logger.warning(f"Business rule violation: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
