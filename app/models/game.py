from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    developer = Column(String)
    active = Column(Boolean, default=True)
    
    # Usando JSONB para melhor performance e suporte a buscas nativas no PostgreSQL
    genres = Column(JSONB) 
    platforms = Column(JSONB)
    images = Column(JSONB)
    system_requirements = Column(JSONB)
