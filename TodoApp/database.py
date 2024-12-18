from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "postgresql://postgres:123456@localhost:5432/TodoApplicationDatabase"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(expire_on_commit=False, autoflush=False, bind=engine)
Base = declarative_base()
