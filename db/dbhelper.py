import databases
import sqlalchemy
from .db_models import *
from bot.config import DATABASE_URL

# DB
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(
    DATABASE_URL#, connect_args={"check_same_thread": False}
)

# session = sqlalchemy.orm.Session(bind=engine)

