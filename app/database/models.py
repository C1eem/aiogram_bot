from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import Optional
from app.database.session import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    name: Mapped[Optional[str]] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(100))

    histories: Mapped[list["History"]] = relationship(back_populates="user")

class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    model: Mapped[str] = mapped_column(String(100))
    user_request: Mapped[str] = mapped_column(String(400))
    model_response: Mapped[str] = mapped_column(String(400))

    user: Mapped["User"] = relationship(back_populates="histories")

