from typing import Optional
from fastapi import status
from fastapi import HTTPException

from events.repository import EventRepository
from events.schemas import CalendarSchema, NewNewsSchema, QuarterSchema


class EventService:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    async def view_all_news(self):
        news = await self.event_repo.get_all_news()
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No news available"
            )

        return news

    async def view_last_news(self):
        news = await self.event_repo.get_last_news()
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No news available"
            )
        return news

    async def post_new_news(self, new_news: NewNewsSchema, user_id: str):
        user = await self.event_repo.get_user_by_id(user_id=user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        news = await self.event_repo.create_news(new_news=new_news, author=user.name)
        return news

    async def view_rating_for_person(self, user_id: str):
        rating = await self.event_repo.get_list_of_completed_tasks(user_id=user_id)

        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No marks yet"
            )

        return rating

    async def view_quarter_average_for_person(
        self, user_id: str, quarter: QuarterSchema
    ) -> Optional[float]:
        quarter_average = await self.event_repo.get_quarter_average(
            user_id=user_id, start_date=quarter.start_date, end_date=quarter.end_date
        )

        if not quarter_average:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No marks found for this period",
            )

        return quarter_average

    async def view_annual_summary(self, user_id: str):
        annual_summary = await self.event_repo.get_annual_summary(user_id=user_id)

        if not annual_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No marks found for this period",
            )

        return annual_summary

    async def view_calendar(self, user_id: str, period: CalendarSchema):
        user_tasks = await self.event_repo.get_users_tasks(
            period_start=period.start, period_end=period.end, user_id=user_id
        )

        user_meetings = await self.event_repo.get_users_meetings(
            period_start=period.start, period_end=period.end, user_id=user_id
        )

        if not user_tasks and not user_meetings:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="No events in this period",
            )

        calendar = {
            "tasks": user_tasks,
            "meetings": user_meetings,
        }

        return calendar


