from sqlalchemy import Column, Enum, ForeignKey, String, Table, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
import uuid
import enum

from shared.database.base import Base
from shared.models.events_models import meeting_participants
from shared.database import uuid_pk, str_64, str_128, str_256


class UsersRoles(enum.Enum):
    SUPERADMIN = "СУПЕРАДМИН"
    TEAM_DIRECTOR = "Директор Команды"
    DEPARTMENT_DIRECTOR = "Управляющий Отделом"
    MANAGER = "Мэнеджер"
    EMPLOYEE = "Работник"


association_table = Table(
    "association_table",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("department_id", ForeignKey("departments.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str_128] # Хэш пароля, а не сам пароль
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    departments = relationship(
        "Department", secondary=association_table, back_populates="employees"
    ) 

    meetings = relationship(
        "Meetings", secondary=meeting_participants, back_populates="participants"
    )

    role: Mapped[UsersRoles] = mapped_column(
        Enum(UsersRoles, name="user_roles"), default=UsersRoles.EMPLOYEE
    )

    def __str__(self):
        return self.name


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    description: Mapped[str_256]

    director_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    director: Mapped["User"] = relationship()

    departments: Mapped[list["Department"]] = relationship(
        "Department", back_populates="team", viewonly=True
    )

    @validates("director")
    def validate_director_role(self, key, user: User):
        if user.role != UsersRoles.TEAM_DIRECTOR:
            raise ValueError(
                f"Директором может быть только пользователь с ролью {UsersRoles.TEAM_DIRECTOR}"
            )
        return user

    def __str__(self):
        return self.name


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    description: Mapped[str_256]

    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"))
    team: Mapped["Team"] = relationship("Team", back_populates="departments")

    employees: Mapped[list["User"]] = relationship(
        secondary=association_table,
        back_populates="departments"
    )

    def __str__(self):
        return self.name
