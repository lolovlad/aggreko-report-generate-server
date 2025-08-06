from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from fastapi import Depends

from ..tables import Equipment
from ..database import get_session


class EquipmentRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self) -> int:
        response = (select(func.count(Equipment.id))
                    .where(Equipment.is_delite == False))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_equip(self, start: int, count: int) -> list[Equipment]:
        response = (select(Equipment)
                    .where(Equipment.is_delite == False)
                    .offset(start)
                    .fetch(count)
                    .order_by(Equipment.id))
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, entity: Equipment):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_by_uuid(self, uuid: str) -> Equipment | None:
        response = select(Equipment).where(Equipment.uuid == uuid).where(Equipment.is_delite == False)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def update(self, entity: Equipment):
        try:
            self.__session.add(entity)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete(self, uuid: str):
        entity = await self.get_by_uuid(uuid)
        if entity is None:
            raise Exception
        try:
            entity.is_delite = True
            self.__session.add(entity)
            await self.__session.commit()
        except Exception:
            await self.__session.rollback()

    async def get_all_equipment(self) -> list[Equipment]:
        response = select(Equipment).where(Equipment.is_delite == False).order_by(
            Equipment.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_equipment_by_uuid_set(self, uuid_list: list[str]) -> list[Equipment]:
        response = select(Equipment).where(Equipment.uuid.in_(uuid_list)).where(Equipment.is_delite == False)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_equipment_by_search_field(self, name_equipment: str) -> list[Equipment]:
        response = (select(Equipment)
                    .where(or_(Equipment.name.ilike(f'%{name_equipment}%'),
                               Equipment.code.ilike(f'%{name_equipment}%')))
                    .where(Equipment.is_delite == False)
                    .order_by(Equipment.id))
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_by_uuid_object_ande_equipment(self, uuid_equipment: str) -> list[Equipment]:
        response = (select(Equipment)
                    .where(Equipment.uuid == uuid_equipment)
                    .where(Equipment.is_delite == False))
        result = await self.__session.execute(response)
        return result.scalars().all()