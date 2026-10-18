from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class WebsiteVisit(Base):
    __tablename__ = "website_visits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    site_key: Mapped[str] = mapped_column(String(100), nullable=False)
    visitor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    page_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referer: Mapped[str | None] = mapped_column(Text, nullable=True)
    visited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )