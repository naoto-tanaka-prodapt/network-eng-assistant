from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(str(settings.DATABASE_URL), echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()