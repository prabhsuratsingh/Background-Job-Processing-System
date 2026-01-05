import uuid
from sqlalchemy import JSON, Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobMetadata(Base):
    __tablename__ = "jobmetadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    status = Column(String, nullable=False)
    job_type = Column(String, nullable=False)

    input_data = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
