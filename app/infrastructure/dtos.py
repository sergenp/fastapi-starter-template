from typing import Generic, List, TypeVar

from pydantic import BaseModel

D = TypeVar("D")


class PaginationDto(BaseModel, Generic[D]):
    total: int
    page: int
    size: int
    results: List[D]
