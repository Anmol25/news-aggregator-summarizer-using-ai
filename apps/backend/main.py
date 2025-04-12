import logger
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.aggregator import router as feed_router
from routers.summarizer import router as summarize_router
from routers.userops import router as user_router
from database.base import Base, engine  # Import Base and engine
from contextlib import asynccontextmanager
from initial_data import seed_data
from sqlalchemy.orm import Session
from database.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they dont exist
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    seed_data(session)
    session.commit()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(summarize_router)
app.include_router(user_router)

origins = ["http://localhost:5173", "http://localhost:3000"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get('/')
def index():
    return {"Welcome To News Aggregator Summarizer api"}
