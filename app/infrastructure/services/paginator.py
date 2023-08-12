from typing import Type

from pydantic import BaseModel
from sqlalchemy import func, select

from app.config import settings
from app.infrastructure.dtos import PaginationDto


class Paginator:
    MAX_PAGE = 2**31 - 1

    @staticmethod
    async def get_paginated_response(
        session,
        qs,
        serializer: Type[BaseModel],
        limit: int = 100,
        page: int = 1,
    ) -> PaginationDto:
        # maximum of 100 items per page
        page_size = min(settings.MAX_PAGE_SIZE, limit)
        # maximum arg for page is 2**31 - 1 to avoid internal server error
        page = min(Paginator.MAX_PAGE, page)
        # get the total count for the query
        count = await session.scalar(select(func.count()).select_from(qs.subquery()))
        # limit offset for given page and limit
        qs = qs.limit(page_size).offset((page - 1) * page_size)
        objects = await session.scalars(qs)
        data = [serializer.model_validate(obj) for obj in objects.unique()]
        return PaginationDto(
            results=data,
            page=page,
            size=page_size,
            total=count,
        )
