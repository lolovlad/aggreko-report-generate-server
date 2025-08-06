from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from fastapi import Depends

from ..tables import *

from ..database import get_session

from datetime import datetime


class EnvRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def get_all_type_user(self) -> list[TypeUser]:
        response = select(TypeUser)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def delete_prof(self, id_prof: int) -> bool:
        response = select(func.count(User.id)).where(User.id_profession == id_prof)
        result = await self.__session.execute(response)
        count = result.scalars().first()
        if count > 0:
            return False
        else:
            prof = await self.__session.get(Profession, id_prof)
            try:
                await self.__session.delete(prof)
                await self.__session.commit()
                return True
            except:
                await self.__session.rollback()
                return False

    '''async def delete_type_equipment(self, id_type_equipment: int) -> bool:
        response = (select(func.count(Equipment.id))
                    .where(Equipment.id_type == id_type_equipment))
        result = await self.__session.execute(response)
        count = result.scalars().first()
        if count > 0:
            return False
        else:
            prof = await self.__session.get(TypeEquipment, id_type_equipment)
            try:
                await self.__session.delete(prof)
                await self.__session.commit()
                return True
            except:
                await self.__session.rollback()
                return False'''

    async def add_list_prof_user(self, prof_users: list[Profession]):
        try:
            self.__session.add_all(prof_users)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def add_prof_user(self, prof: Profession) -> Profession:
        try:
            self.__session.add(prof)
            await self.__session.commit()
            return prof
        except:
            await self.__session.rollback()
            return None

    async def get_prof_by_name(self, prof_name: str) -> Profession | None:
        response = select(Profession).where(Profession.name == prof_name)
        result = await self.__session.execute(response)
        return result.scalars().one()

    async def get_all_prof_user(self) -> list[Profession]:
        response = select(Profession)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_type_equip(self) -> list[TypeEquipment]:
        response = select(TypeEquipment)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add_list_type_equipment(self, type_equ: list[TypeEquipment]):
        try:
            self.__session.add_all(type_equ)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def get_state_claim(self) -> list[StateClaim]:
        response = select(StateClaim)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def add(self, entity):
        try:
            self.__session.add(entity)
            await self.__session.commit()
            return entity
        except:
            await self.__session.rollback()
            return None

    async def get_all_type_blueprint(self) -> list[TypeBlueprint]:
        response = select(TypeBlueprint)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_type_equipment_blueprint(self) -> list[TypeEquipmentBlueprint]:
        response = select(TypeEquipmentBlueprint)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_all_type_device(self) -> list[TypeDevice]:
        response = select(TypeDevice)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_state_claim_by_system_name(self, system_name: str):
        response = select(StateClaim).where(StateClaim.system_name == system_name)
        result = await self.__session.execute(response)
        return result.scalars().one()


