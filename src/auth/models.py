from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from database import uuid_pk, str_64


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str_64]