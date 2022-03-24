import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./torlist.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

whitelisted_ips = sqlalchemy.Table(
    "whitelisted_ips",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("ip", sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
