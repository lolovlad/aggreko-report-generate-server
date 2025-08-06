from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..tables import Blueprint
from ..database import get_session

from fastapi import Depends


class BlueprintRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self) -> int:
        response = select(func.count(Blueprint.id))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit(self, start: int, count: int) -> list[Blueprint]:
        response = select(Blueprint).offset(start).fetch(count).order_by(Blueprint.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_by_uuid(self, uuid: str) -> Blueprint:
        response = select(Blueprint).where(Blueprint.uuid == uuid)
        result = await self.__session.execute(response)
        return result.scalars().one()

    async def get_by_search_field(self, name: str) -> list[Blueprint]:
        response = select(Blueprint).where(and_(
            Blueprint.name.ilike(f'%{name}%')
        )).order_by(Blueprint.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, data: Blueprint):
        try:
            self.__session.add(data)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception