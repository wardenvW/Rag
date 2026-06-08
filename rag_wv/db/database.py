from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(url=DATABASE_URL)

class Base(DeclarativeBase):
    pass

def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session