from collections import defaultdict
from typing import Dict, List, Type

from pydantic import BaseModel

from app.infrastructure.event_handlers.base_event_handler import BaseEventHandler


class Mediator:
    events_map: Dict[Type[BaseModel], List[BaseEventHandler]] = defaultdict(list)

    @classmethod
    def register(cls, event_type: Type[BaseModel], handler: BaseEventHandler) -> None:
        cls.events_map[event_type].append(handler)

    @classmethod
    async def send(cls, event: BaseModel) -> None:
        for handler in cls.events_map[event.__class__]:
            await handler.handle(event)
