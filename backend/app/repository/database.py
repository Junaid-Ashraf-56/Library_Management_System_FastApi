from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

def init_db():
    Base.metadata.create_all(bind=engine)