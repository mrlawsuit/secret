from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends

from app.repositories import secret_repository as secret_db
import schemas as shm
import models
from database import init_db, dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print('Database is successfully initiated')

    yield

    await dispose_engine()


app = FastAPI(lifespan=lifespan)


@app.post('/generate', response_model=shm.SecretKeyResponse)
async def generate_secret(
    secret: shm.SecretCreate
):
    '''Generate secret key for a one-time secret.'''
    secret_key = await secret_db.create_secret(secret)
    return {'secret_key': secret_key}


@app.get('/secrets/{secret_key}')
async def get_secret(secret_key: str, passphrase: str):
    '''Recieve and decrypt a one-time secret usinfg secret key and passphrase'''
    pass
