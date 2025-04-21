from datetime import date, datetime
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class NewNewsSchema(BaseModel):
    title: Annotated[str, Field()]
    text: Annotated[str, Field()]
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Break NEWS",
            "text": "ABC",
        }
    })

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
    assignee_rating: int
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