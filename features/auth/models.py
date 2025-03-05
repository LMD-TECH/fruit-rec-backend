# Models
from core.dbconfig import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_utilisateur = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_profile = Column(String, nullable=True)
    nom_famille = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    numero_telephone = Column(String, unique=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    code_otp = Column(String, nullable=True)
    code_otp_expiration = Column(DateTime, nullable=True)
    date_creation_compte = Column(DateTime, default=datetime.utcnow)
    date_mise_a_jour = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # historiques = relationship("Historique", back_populates="utilisateur")


# user = Utilisateur().activites
