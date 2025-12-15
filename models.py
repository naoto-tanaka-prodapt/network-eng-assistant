from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class History(Base):
  __tablename__ = 'history'
  id = Column(Integer, primary_key=True)
  symptom = Column(String, nullable=False)
  resolution = Column(String, nullable=False)
  user_feedback = Column(String, nullable=False)
  guide = Column(String, nullable=False)