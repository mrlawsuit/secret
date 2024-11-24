from datetime import datetime, UTC
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import schemas as shm
import utils
from app.repositories import secret_repository as secret_db
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
    '''
    Generate secret key for a one-time secret.
    '''

    secret_key = await secret_db.create_secret(secret)
    return {'secret_key': secret_key}


@app.get('/secrets/{secret_key}', response_model=shm.SecretResponse)
async def get_secret(secret_key: str, passphrase: str):
    '''
    Recieve and decrypt a one-time secret usinfg secret key and passphrase
    '''

    password_mgr = utils.PasswordManager()
    secret_mgr = utils.SecretManager(passphrase)
    secret = await secret_db.get_secret(secret_key)
    if not secret:
        raise HTTPException(status_code=404, detail='Secret not found')
    if secret.consumed:
        raise HTTPException(
            status_code=410,
            detail='Secret has already been consumed'
        )
    if secret.expires_at and secret.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=410, detail='Secret has expired')
    if not password_mgr.verify_password(passphrase, secret.passphrase_hash):
        raise HTTPException(status_code=403, detail='Invalid passphrase')
    decrypted_secret = secret_mgr.decrypt_secret(secret.secret_data)
    await secret_db.make_consume_mark(secret)
    return {'secret': decrypted_secret}
