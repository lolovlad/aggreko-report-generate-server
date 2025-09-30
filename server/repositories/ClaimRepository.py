from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, or_
from ..tables import Claim, User, StateClaim
from ..database import get_session

from fastapi import Depends


class ClaimRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self) -> int:
        response = select(func.count(Claim.id))
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_user(self, start: int, count: int) -> list[Claim]:
        response = select(Claim).offset(start).fetch(count).order_by(Claim.id)
        result = await self.__session.execute(response)
        return result.scalars().all()

    async def get_limit_admin(self,
                              start: int,
                              count: int) -> list[Claim]:
        response = select(Claim).join(StateClaim)
        #if uuid_object != "all":
        #    response = response.where(Object.uuid == uuid_object)
        #if id_state_claim != 0:
        #    response = response.where(Claim.id_state_claim == id_state_claim)
        response = response.where(or_(StateClaim.system_name == "accepted", StateClaim.system_name == "under_consideration"))
        response = response.offset(start).fetch(count).order_by(Claim.id)
        result = await self.__session.execute(response)
        return result.scalars().unique().all()

    async def get_by_uuid(self, uuid: str) -> Claim:
        response = select(Claim).where(Claim.uuid == uuid)
        result = await self.__session.execute(response)
        return result.scalars().one()

    async def add(self, data: Claim):
        try:
            self.__session.add(data)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

    async def delete(self, claim: Claim):
        try:
            await self.__session.refresh(claim)
            await self.__session.delete(claim)
            await self.__session.commit()
        except:
            await self.__session.rollback()
            raise Exception

