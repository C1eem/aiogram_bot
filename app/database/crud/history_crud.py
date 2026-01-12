from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import History

class HistoryCRUD:
    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        history = History(**kwargs)
        session.add(history)
        await session.commit()
        await session.refresh(history)
        return history

    @staticmethod
    async def get_history(session: AsyncSession, user_id: int):
        result = await session.execute(
            select(History)
            .where(History.user_id == user_id)
            .order_by(History.id.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def delete(session: AsyncSession, user_id: int):
        await session.execute(
            delete(History).where(History.user_id == user_id)
        )
        await session.commit()