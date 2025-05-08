from decimal import Decimal
from typing import Annotated
from sqlalchemy import Integer, Numeric, String
import uuid
from sqlalchemy.orm import mapped_column


uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, default=uuid.uuid4),
]

int32_pk = Annotated[
    int,
    mapped_column(
        Integer,
        primary_key=True,
    ),
]
numeric_10_2 = Annotated[Decimal, mapped_column(Numeric(precision=10, scale=2))]
str_128 = Annotated[str, mapped_column(String(128))]
str_256 = Annotated[str, mapped_column(String(156))]
str_64 = Annotated[str, mapped_column(String(64))]
