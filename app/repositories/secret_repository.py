from datetime import datetime, timedelta, UTC
import uuid

from sqlalchemy import select

from app import database as db
import app.schemas as shm
import app.utils as utils
from app import models


async def create_secret(secret: shm.SecretCreate) -> str:
    '''Create record in db with new secret'''
    secret_key = str(uuid.uuid4())
    passphrase_hash = utils.get_password_hash(secret.passphrase)
    encrypted_secret = utils.encrypt_secret(secret.secret, secret.passphrase)
    expires_at = None
    if secret.ttl:
        expires_at = datetime.now(UTC) + timedelta(seconds=secret.ttl)
    db_secret = models.Secret(
        id=str(uuid.uuid4()),
        secret_key=secret_key,
        secret_data=encrypted_secret,
        passphrase_hash=passphrase_hash,
        expires_at=expires_at,
    )
    async with db.async_session() as session:
        session.add(db_secret)
        await session.commit()
    return secret_key


async def get_secret(secret_key: str):
    '''Get a secret by its secret key'''
    async with db.async_session() as session:
        result = await session.execute(
            select(models.Secret).
            where(models.Secret.secret_key == secret_key)
        )
    return result.scalars().first()


