from pydantic import BaseModel


class CustomerBase(BaseModel):
    """Base com campos compartilhados entre Input e Output."""

    name: str
