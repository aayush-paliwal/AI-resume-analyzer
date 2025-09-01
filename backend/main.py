from routes import resume
from db import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ❌ This won't work with AsyncEngine
# Base.metadata.create_all(bind=engine)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run to.run(create_tables())

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.get("/")
async def root():
    return { "message": "API is working fine" }

app.include_router(resume.router, prefix="/api/v1")