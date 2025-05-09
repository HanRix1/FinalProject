from enum import Enum


class TaskStatus(Enum):
    OPEN = "Открыто"
    IN_PROGRESS = "В работе"
    DONE = "Выполнено"


class EventType(Enum):
    TASK = "Задача"
    MEET = "Встреча"
