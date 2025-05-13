from datetime import date, datetime
from typing import Optional
from sqlalchemy import desc, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from events.schemas import NewNewsSchema
from shared.models.auth_models import Department, User
from shared.models.events_models import (
    Marks,
    News,
    Meetings,
    Tasks
)


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_news(self, new_news: NewNewsSchema, author: str) -> News:
        new_news = News(title=new_news.title, text=new_news.text, author=author)

        self.session.add(new_news)
        await self.session.commit()

        await self.session.refresh(new_news)
        return new_news

    async def get_all_news(self) -> list[News] | None:
        query = select(News).order_by(desc(News.created_at))
        news = (await self.session.scalars(query)).all()
        return news

    async def get_last_news(self) -> News | None:
        query = select(News).order_by(desc(News.created_at)).limit(1)
        news = await self.session.scalar(query)
        return news

    async def get_user_by_id(self, user_id: str) -> User:
        query = select(User).where(User.id == user_id)
        user = await self.session.scalar(query)
        return user

    async def get_list_of_completed_tasks(self, user_id: str) -> list[Marks]:
        query = (
            select(Marks)
            .where(Marks.assignee_id == user_id)
            .order_by(Marks.task_deadline)
        )
        rating = await self.session.scalars(query)
        return rating.all()

    async def get_quarter_average(
        self, user_id: str, start_date: date, end_date: date
    ) -> Optional[float]:
        query = select(func.avg(Marks.assignee_rating)).where(
            and_(
                Marks.assignee_id == user_id,
                Marks.task_deadline < end_date,
                Marks.task_deadline >= start_date,
            )
        )
        quarter_average = await self.session.scalar(query)
        return quarter_average

    async def get_annual_summary(self, user_id: str) -> Optional[float]:
        department_id_subq = (
            select(Department.id)
            .join(Department.employees)
            .where(User.id == user_id)
            .limit(1)
            .scalar_subquery()
        )

        query = select(func.avg(Marks.assignee_rating)).where(
            Marks.assignee_id.in_(
                select(User.id)
                .join(User.departments)
                .where(Department.id == department_id_subq)
            )
        )

        annual_summary = await self.session.scalar(query)
        return annual_summary

    async def get_users_meetings(
        self, period_start: datetime, period_end: datetime, user_id: str
    ) -> list[Meetings] | None:
        query = (
            select(Meetings)
            .join(Meetings.participants)
            .where(
                and_(
                    User.id == user_id,
                    Meetings.start_at < period_end,
                    Meetings.start_at >= period_start,
                )
            )
            .order_by(Meetings.start_at)
        )

        meetings = await self.session.scalars(query)
        return meetings.all()

    async def get_users_tasks(
        self, period_start: datetime, period_end: datetime, user_id: str
    ) -> list[Tasks] | None:
        query = (
            select(Tasks)
            .where(
                and_(
                    Tasks.assignee_id == user_id,
                    Tasks.deadline < period_end,
                    Tasks.deadline >= period_start,
                )
            )
            .order_by(Tasks.deadline)
        )

        tasks = await self.session.scalars(query)
        return tasks.all()
