from contextlib import contextmanager
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from src.db.table import Base
from src.config import SQL_TABLENAME

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
    metadata = Base.metadata

    for tbname in SQL_TABLENAME:
        if not inspect(engine).has_table(tbname):
            Base.metadata.create_all(engine)

    yield session

    session.close()