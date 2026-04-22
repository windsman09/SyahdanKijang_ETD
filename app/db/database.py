from sqlalchemy import create_engine
from sqlalchemy.opr, import declarative_base

DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/db_name"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)
Base = declarative_base()
