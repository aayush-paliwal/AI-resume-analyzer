import os
import ssl

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("Database URL not provided")


# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},echo=True
# )


ssl_context = ssl.create_default_context()

# Create the async engine (note: echo=True logs SQL queries)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"ssl": ssl_context})

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create session factory using AsyncSession
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# Dependency to use in routes
async def get_db():
    async with SessionLocal() as session:
        yield session
        