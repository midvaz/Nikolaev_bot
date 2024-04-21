from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# DB_URL = "postgresql+asyncpg://postgres:postgres@alert_pg:4000/postgres" # для докера
# TODO: ПОМЕНЯТЬ LOCALHOST
DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:4000/postgres" # для локалки
engine = create_async_engine(DB_URL, echo=False)
session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

