from typing import Annotated
from fastapi import Depends

from events.repository import EventRepository
from events.services import EventService
from shared.dependencies import DataBaseSessionDep


def get_event_repo(session: DataBaseSessionDep) -> EventRepository:
    return EventRepository(session)


def get_event_service(
    event_repo: EventRepository = Depends(get_event_repo),
) -> EventService:
    return EventService(event_repo)


EventServiceDep = Annotated[EventService, Depends(get_event_service)]
