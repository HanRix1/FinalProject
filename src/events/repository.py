from datetime import date, datetime
from sqlalchemy import desc, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User, association_table, Department
from events.models import Marks, News, Meetings, meeting_participants
from events.schemas import NewNewsSchema


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_news(self, new_news: NewNewsSchema, author: str) -> News:
        new_news = News(
            title=new_news.title,
            text=new_news.text,
            author=author
        )
            
        self.session.add(new_news)
        await self.session.commit()
    
        await self.session.refresh(new_news)
        return new_news
    
    async def get_all_news(self) -> list[News] | None:
        query = (
            select(News)
            .order_by(News.created_at)
        )
        news = await self.session.scalars(query)
        return news
    
    async def get_last_news(self) -> News | None:
        query = (
            select(News)
            .order_by(desc(News.created_at))
            .limit(1)
        )
        news = await self.session.scalar(query)
        return news
    
    async def get_user_by_id(self, user_id: str) -> User:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        user = await self.session.scalar(query)
        return user
    
    async def get_list_of_completed_tasks(self, user_id: str) -> list[Marks]:
        query = (
            select(Marks)
            .where(Marks.assignee_id == user_id)
            .order_by(Marks.task_deadline)
        )
        raiting = await self.session.scalars(query)
        return raiting

    async def get_quarter_avarage(
            self, 
            user_id: str, 
            start_date: date, 
            end_date: date
    ) -> float | None:
        query = (
            select(func.avg(Marks.assignee_rating))
            .where(
                and_(
                    Marks.assignee_id == user_id,
                    Marks.task_deadline < end_date,
                    Marks.task_deadline >= start_date
                )
            )
        )
        quarter_avarage = await self.session.scalar(query)
        return quarter_avarage

    async def get_annual_summary(self, user_id: str) -> float | None:
        query = (
            select(func.avg(Marks.assignee_rating))
            .where(Marks.assignee_id.in_(
                select(association_table.c.user_id)
                .where(association_table.c.department_id == select(
                    association_table.c.department_id)
                    .where(association_table.c.user_id == user_id)
                    .limit(1)
                    .scalar_subquery()
                )
            )
        ))

        annual_summary = await self.session.scalar(query)
        return annual_summary


async def get_team_members_query(user_id: str):
    team_id_subq = (
        select(Department.team_id)
        .join(association_table, Department.id == association_table.c.department_id)
        .where(association_table.c.user_id == user_id)
        .limit(1)
        .scalar_subquery()
    )

    stmt = (
        select(User)
        .join(association_table, User.id == association_table.c.user_id)
        .join(Department, Department.id == association_table.c.department_id)
        .where(Department.team_id == team_id_subq)
        .distinct()
    )

    return stmt

async def get_users_with_existing_meetings():
    qurey = (
        select(Meetings.start_at, Meetings.duration, meeting_participants.c.user_id, User.name)
        .join(meeting_participants, Meetings.id == meeting_participants.c.meeting_id)
        .join(User, User.id == meeting_participants.c.user_id)
    )
    return qurey
