from datetime import datetime, timezone
import uuid
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Mixin adding created_at timestamp to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )
