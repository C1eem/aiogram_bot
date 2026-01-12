from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserCRUD:

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        user = User(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int):
        return await session.get(User, user_id)

    @staticmethod
    async def get_by_tg_id(session: AsyncSession, tg_id: int):
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_model(session: AsyncSession, tg_id: int):
        result = await session.execute(
            select(User.model).where(User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, tg_id: int, **kwargs):
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(**kwargs)
        )
        await session.commit()

        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_model(session: AsyncSession, tg_id: int, model: str):
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(model=model)
        )
        await session.commit()

        user = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return user.scalar_one_or_none()


    @staticmethod
    async def get_all_users(session: AsyncSession):
        result = await session.execute(select(User).order_by(User.tg_id))
        return result.scalars().all()