from pydantic import BaseModel, ConfigDict

from src.domain.entities.customer import Customer
from src.usecases.v1.schemas.api.customer import CustomerCreate


class CustomerRegistrationContext(BaseModel):
    """Contexto compartilhado entre os handlers da criação de cliente."""

    dto: CustomerCreate
    customer: Customer | None = None

    # Permite armazenar a Entidade de Domínio (que não é Pydantic)
    model_config = ConfigDict(arbitrary_types_allowed=True)
