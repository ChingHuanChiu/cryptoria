from contextlib import contextmanager
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()


@contextmanager
def get_db_session():

    
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    db_name = os.getenv("DB_NAME")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    
    engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{db_name}", pool_size=10, max_overflow=0)
    session = Session(engine)
    yield session

    session.close()
