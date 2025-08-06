from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, or_
from ..tables import Claim, User, StateClaim
from ..database import get_session

from fastapi import Depends


class ClaimRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def count_row(self, id_user: int | None) -> int:
        response = select(func.count(Claim.id))
        if id_user is not None:
            response = response.where(Claim.id_user == id_user)
        result = await self.__session.execute(response)
        return result.scalars().first()

    async def get_limit_user(self, id_user: int, start: int, count: int) -> list[Claim]:
        response = select(Claim).where(Claim.id_user == id_user).offset(start).fetch(count).order_by(Claim.id)
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
        #try:
        self.__session.add(data)
        await self.__session.commit()
        #except:
        #    await self.__session.rollback()
        #    raise Exception

