from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from core.dbconfig import Base


class Historique(Base):
    __tablename__ = "historique"

    id_historique = Column(UUID(as_uuid=True),
                           primary_key=True, default=uuid.uuid4)
    nbre_total_img = Column(Integer, nullable=False)
    date_televersement = Column(DateTime, default=datetime.now)
    description = Column(String, nullable=False)

    id_utilisateur = Column(
        UUID(as_uuid=True), ForeignKey("utilisateur.id_utilisateur"))

    # Relation avec Image : un historique peut avoir plusieurs images
    images = relationship(
        "Image", back_populates="historique", cascade="all, delete-orphan")
