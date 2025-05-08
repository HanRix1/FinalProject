from shared.models.auth_models import Department, Team, User, association_table
from shared.models.events_models import (
    News,
    Marks,
    Tasks,
    Meetings,
    meeting_participants,
)


__all__ = [
    "Department",
    "Team",
    "User",
    "association_table",
    "News",
    "Marks",
    "Tasks",
    "Meetings",
    "meeting_participants",
]
