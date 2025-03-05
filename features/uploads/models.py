# Models
from core.dbconfig import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime


class Image(Base):
    __tablename__ = "image"

    id_image = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_path = Column(String, nullable=False)
