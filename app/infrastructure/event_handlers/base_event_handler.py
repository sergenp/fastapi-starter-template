from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseEventHandler(ABC):
    @abstractmethod
    async def handle(self, event: BaseModel) -> None:
        raise NotImplementedError()
