from contextlib import asynccontextmanager
from fastapi import FastAPI
from handlers.miners import router
from database.crud import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    app.include_router(router)
    yield
    await db.close()


app = FastAPI(lifespan=lifespan)