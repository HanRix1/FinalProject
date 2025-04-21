from fastapi import status
from fastapi import HTTPException
from events.repository import EventRepository
from events.schemas import NewNewsSchema, QuarterSchema


class EventService:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo
        
    async def view_all_news(self):
        news = await self.event_repo.get_all_news()
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No news available"
            )

        return news

    async def view_last_news(self):
        news = await self.event_repo.get_last_news()
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No news available"
            )
        return news


    async def post_new_news(self, new_news: NewNewsSchema, user_id: str):
        user = await self.event_repo.get_user_by_id(user_id=user_id)
        news = await self.event_repo.create_news(new_news=new_news, author=user.name)
        return news
    
    async def view_rating_for_person(self, user_id: str):
        raiting = await self.event_repo.get_list_of_completed_tasks(user_id=user_id)

        if not raiting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No marks yet"
            )
    
        return raiting
        
    async def view_quarter_avarage_for_person(self, user_id: str, quarter: QuarterSchema) -> str:
        quarter_avarage = await self.event_repo.get_quarter_avarage(
            user_id=user_id, 
            start_date=quarter.start_date,
            end_date=quarter.end_date
        )

        if not quarter_avarage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No marks found for this period"
            )
        
        return quarter_avarage
    
    async def view_annual_summary(self, user_id: str):
        annual_summary = await self.event_repo.get_annual_summary(user_id=user_id)

        if not annual_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No marks found for this period"
            )
        
        return annual_summary