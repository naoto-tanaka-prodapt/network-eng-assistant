from sqlalchemy import create_engine
from config import settings
from sqlalchemy.orm import sessionmaker
from config import settings

def get_session():
  engine = create_engine(str(settings.DATABASE_URL), echo=not settings.PRODUCTION)
  db = sessionmaker(bind=engine)()
  try:
      yield db
  finally:
      db.close()