from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    category = Column(String, nullable=False)

    location = Column(String, nullable=False)

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String,
        default="REPORTED",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )