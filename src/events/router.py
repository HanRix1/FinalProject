from typing import Annotated
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from auth.dependencies import AuthServiceDep
from events.dependencies import EventServiceDep
from events.schemas import CalendarOut, NewNewsSchema, NewsOut, QuarterSchema, RainitgOut, CalendarSchema

router = APIRouter(
    prefix="/event"
)


@router.post("/send-message", tags=["news"])
async def send_message(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request,
    new_news: Annotated[NewNewsSchema, Body()]
):
    user_id = await auth_service.check_autorization(request=request)
    news = await event_service.post_new_news(new_news=new_news, user_id=user_id)
    return JSONResponse({"message": "News was Published"})

@router.get("/get-last-news", tags=["news"], response_model=NewsOut)
async def get_last_message(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request
):
    user_id = await auth_service.check_autorization(request=request)
    news = await event_service.view_last_news()
    return news

@router.get("/get-news", tags=["news"], response_model=list[NewsOut])
async def get_news(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request
):
    user_id = await auth_service.check_autorization(request=request)
    news = await event_service.view_all_news()
    return news
    


@router.get("/rating-matrix", tags=["tasks"], response_model=list[RainitgOut])
async def get_personal_rating_matrix(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request
):
    user_id = await auth_service.check_autorization(request=request)
    raintg = await event_service.view_rating_for_person(user_id=user_id)
    return raintg


@router.get("/quarter-avg", tags=["tasks"])
async def get_personal_quarter_avg(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request,
    quarter: Annotated[QuarterSchema, Depends()]
):
    user_id = await auth_service.check_autorization(request=request)
    quarter_avg = await event_service.view_quarter_avarage_for_person(user_id=user_id, quarter=quarter)
    return quarter_avg


@router.get("/annual-summary", tags=["tasks"])
async def get_personal_annual_summary(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request
):
    user_id = await auth_service.check_autorization(request=request)
    annual_summary = await event_service.view_annual_summary(user_id=user_id)
    return annual_summary



@router.get("/calendar", tags=["calendar"], response_model=CalendarOut)
async def get_monthly_calendar(
    event_service: EventServiceDep,
    auth_service: AuthServiceDep,
    request: Request,
    period: Annotated[CalendarSchema, Depends()]
):
    user_id = await auth_service.check_autorization(request=request)
    tasks = await event_service.view_calendar(user_id=user_id, period=period)
    return tasks 

    