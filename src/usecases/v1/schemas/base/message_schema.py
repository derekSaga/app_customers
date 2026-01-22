import dataclasses
import uuid
from datetime import datetime
from typing import Any, Self, TypeVar

from pydantic import BaseModel, Field

from src.domain.entities.message import Message


class MessageHeader(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    content_type: str = "application/json"
    schema_version: str = "1.0"


TPayload = TypeVar("TPayload", bound=BaseModel)


class MessagePydantic[TPayload](BaseModel):
    header: MessageHeader
    payload: TPayload

    @classmethod
    def from_entity(cls, entity: Message[Any]) -> Self:
        # Garante a conversão do header que é obrigatoriamente uma dataclass
        header_dict = dataclasses.asdict(entity.header)

        # Lógica para o payload
        payload_data = entity.payload
        if dataclasses.is_dataclass(payload_data) and not isinstance(
            payload_data, type
        ):
            payload_data = dataclasses.asdict(payload_data)

        return cls.model_validate(
            {
                "header": header_dict,
                "payload": payload_data,
            }
        )
