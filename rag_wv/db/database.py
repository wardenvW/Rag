from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from dotenv import load_dotenv
import os, logging

load_dotenv()
logger = logging.getLogger(__name__)

logger.info("Getting DataBaseURL")
DATABASE_URL = os.getenv("DATABASE_URL")
logger.debug(f"GOT: {DATABASE_URL}")

logger.info("Creating engine")
engine = create_engine(url=DATABASE_URL)

class Base(DeclarativeBase):
    pass

def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session