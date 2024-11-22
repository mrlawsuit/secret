from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import func


class Base(AsyncAttrs, DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Secret(Base):
    '''DB model for storing secrets'''

    __tablename__ = 'secrets'

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    secret_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )
    secret_data: Mapped[str] = mapped_column(String, nullable=False)
    passphrase_hash: Mapped[str] = mapped_column(String, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_att: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
