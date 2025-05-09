from datetime import datetime, time
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Time, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shared.models.auth_models import User
from events.utils import TaskStatus
from shared.database.base import Base
from shared.database import uuid_pk, str_64, str_128, str_256


class News(Base):
    __tablename__ = "news"

    id: Mapped[uuid_pk]
    title: Mapped[str_64]
    text: Mapped[str_256]
    author: Mapped[str_128]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Marks(Base):
    __tablename__ = "marks"

    id: Mapped[uuid_pk]
    task_description: Mapped[str_256]
    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    assignee_user: Mapped["User"] = relationship()
    assignee_rating: Mapped[int] = mapped_column(Integer, nullable=True)
    task_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid_pk]
    description: Mapped[str_256]
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), default=TaskStatus.OPEN
    )
    coments: Mapped[str_256]
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    assignee: Mapped["User"] = relationship()


meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("meeting_id", ForeignKey("meetings.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Meetings(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid_pk]
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration: Mapped[time] = mapped_column(Time)
    theme: Mapped[str_128]
    participants: Mapped[list["User"]] = relationship(secondary=meeting_participants)
