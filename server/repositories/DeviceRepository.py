from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..tables import Device, TypeDevice
from ..database import get_session

from fastapi import Depends


class DeviceRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self) -> int:
        response = select(func.count(Device.id))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit(self, start: int, count: int) -> list[Device]:
        response = select(Device).offset(start).fetch(count).order_by(Device.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, data: Device):
        try:
            self.__session.add(data)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_device_by_id(self, id_device: int) -> Device:
        response = select(Device).where(Device.id == id_device)
        result = await self.__session.execute(response)
        return result.scalars().one()

    async def get_device_by_search_field(self, name: str) -> list[Device]:
        response = select(Device).where(Device.name.ilike(f'%{name}%'),).order_by(Device.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def update(self, data: Device):
        try:
            self.__session.add(data)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete(self, id_device: str):
        entity = await self.get_device_by_id(id_device)
        entity.is_deleted = True

        await self.__session.commit()

    async def get_device_by_code(self, code: str) -> list[Device]:
        response = select(Device).where(Device.code == code)
        result = await self.__session.execute(response)
        return result.scalars().all()
