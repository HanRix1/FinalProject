from datetime import date, datetime, time, timedelta
from typing import Annotated, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
import enum

from events.utils import TaskStatus


class NewNewsSchema(BaseModel):
    title: Annotated[str, Field()]
    text: Annotated[str, Field()]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Break NEWS",
                "text": "ABC",
            }
        }
    )


class NewsOut(BaseModel):
    id: UUID
    title: str
    text: str
    author: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RainitgOut(BaseModel):
    id: UUID
    task_description: str
    assignee_rating: int | None
    task_deadline: datetime

    model_config = ConfigDict(from_attributes=True)


class QuarterSchema(BaseModel):
    year: int
    quarter: Annotated[int, Field(gt=0, lt=5)]

    @property
    def start_date(self) -> date:
        return date(self.year, (self.quarter - 1) * 3 + 1, 1)

    @property
    def end_date(self) -> date:
        if self.quarter == 4:
            return date(self.year + 1, 1, 1)
        return date(self.year, self.quarter * 3 + 1, 1)


class Period(str, enum.Enum):
    DAY = "Day"
    WEEK = "Month"


class CalendarSchema(BaseModel):
    period: Period

    @property
    def start(self) -> datetime:
        data = datetime.now()

        if self.period == "Day":
            return data.replace(hour=0, minute=0, second=0, microsecond=0)
        return data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @property
    def end(self) -> date:
        data = datetime.now()
        if self.period == "Day":
            return data.replace(hour=23, minute=59, second=59, microsecond=999999)

        next_month = data.replace(day=28) + timedelta(days=4)
        current_month = (next_month - timedelta(days=next_month.day)).month
        return data.replace(
            month=current_month, hour=23, minute=59, second=59, microsecond=999999
        )


class TasksOut(BaseModel):
    status: TaskStatus
    description: str
    coments: str
    deadline: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingsOut(BaseModel):
    start_at: datetime
    duration: time
    theme: str

    model_config = ConfigDict(from_attributes=True)


class CalendarOut(BaseModel):
    tasks: Union[list[TasksOut], None] = None
    meetings: Union[list[MeetingsOut], None] = None
