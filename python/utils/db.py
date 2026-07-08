from sqlalchemy import create_engine
from config.settings import DATABASE_URL

def get_engine():
    """
    Returns a SQLAlchemy engine — the reusable connection pool
    every other script in the pipeline should import and use.
    Don't create a new engine per script; import this one.
    """
    return create_engine(DATABASE_URL)