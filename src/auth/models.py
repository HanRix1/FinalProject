from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from sqlalchemy.orm import relationship
from database import uuid_pk, str_64, str_128, str_256
import uuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str_128]
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Roles"] = relationship()
    
class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[uuid_pk]
    title: Mapped[str_64]
    description: Mapped[str_256] 