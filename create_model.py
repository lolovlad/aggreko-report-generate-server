from sqlalchemy import select, func
from asyncio import run
from server.database import async_session
from server.tables import (User,
                           TypeUser,
                           Profession,
                           StateClaim)
from uuid import uuid4


async def create_prof():
    async with async_session() as session:
        try:
            response = select(func.count(Profession.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                prof = Profession(
                    system_name="unknown",
                    name="Неизвестно"
                )

                session.add(prof)
                await session.commit()
        finally:
            await session.close()


async def create_user_contest():
    async with async_session() as session:
        try:
            response = select(func.count(TypeUser.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                super_admin_type = TypeUser(
                    system_name="super_admin",
                    name="Супер админ"
                )
                admin_type = TypeUser(
                    system_name="admin",
                    name="Админ"
                )
                user_type = TypeUser(
                    system_name="user",
                    name="Пользователь"
                )
                session.add(admin_type)
                session.add(user_type)
                session.add(super_admin_type)
                await session.commit()
            response = select(func.count(User.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                admin_user = User(
                    email="vladislav.skripnik@aggreko-eurasia.ru",
                    id_type=super_admin_type.id,
                    id_profession=1
                )
                admin_user.password = "admin"
                session.add(admin_user)
                await session.commit()
        finally:
            await session.close()


async def create_state_claim_context():
    async with async_session() as session:
        try:
            response = select(func.count(StateClaim.id))
            result = await session.execute(response)
            count = result.scalars().first()
            if count == 0:
                one = StateClaim(
                    system_name="under_consideration",
                    name="На рассмотрении"
                )
                two = StateClaim(
                    system_name="under_development",
                    name="На доработку"
                )

                threa = StateClaim(
                    system_name="accepted",
                    name="Принято"
                )
                ttt = StateClaim(
                    system_name="draft",
                    name="Черновик"
                )

                session.add(one)
                session.add(two)
                session.add(threa)
                session.add(ttt)
                await session.commit()
        finally:
            await session.close()


async def main():
    await create_prof()
    await create_user_contest()
    await create_state_claim_context()

run(main())