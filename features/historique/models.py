# Models
from core.dbconfig import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime


class Historique(Base):
    __tablename__ = "historique"

    id_historique = Column(UUID(as_uuid=True),
                           primary_key=True, default=uuid.uuid4)
    nbre_total_img = Column(Integer, nullable=False)
    date_televersement = Column(DateTime, default=datetime.utcnow)
    description = Column(JSON, nullable=False)

    id_utilisateur = Column(
        UUID(as_uuid=True), ForeignKey("utilisateur.id_utilisateur"))
    utilisateur = relationship("Utilisateur", back_populates="activites")

    images = relationship("Image", back_populates="historique")
