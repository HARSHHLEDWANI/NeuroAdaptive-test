from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create the engine (the connection factory)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 2. Create the SessionLocal class
# Each request will create its own database session from this factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Dependency Injection
# This function will be used in every API endpoint to get a DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
