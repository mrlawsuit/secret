from datetime import datetime, timedelta, UTC
import uuid

from sqlalchemy import select

from app import database as db
from app import schemas as shm
from app import utils
from app import models


class SecretFactory:
    @staticmethod
    def create(secret: shm.SecretCreate) -> models.Secret:
        '''
        Factory method for creating instance of secret model
        '''

        password_mgr = utils.PasswordManager()
        secret_mgr = utils.SecretManager(secret.passphrase)
        secret_key = str(uuid.uuid4())
        passphrase_hash = password_mgr.get_password_hash(secret.passphrase)
        encrypted_secret = secret_mgr.encrypt_secret(secret.secret)
        expires_at = None
        if secret.ttl:
            expires_at = datetime.now(UTC) + timedelta(seconds=secret.ttl)
        return models.Secret(
            id=str(uuid.uuid4()),
            secret_key=secret_key,
            secret_data=encrypted_secret,
            passphrase_hash=passphrase_hash,
            expires_at=expires_at
        )


async def create_secret(secret: shm.SecretCreate) -> str:
    '''
    Create record in db with new secret
    '''

    db_secret = SecretFactory.create(secret)
    secret_key = db_secret.secret_key
    async with db.async_session() as session:
        session.add(db_secret)
        await session.commit()
    return secret_key


async def get_secret(secret_key: str) -> models.Secret:
    '''
    Get a secret by its secret key
    '''

    async with db.async_session() as session:
        result = await session.execute(
            select(models.Secret).
            where(models.Secret.secret_key == secret_key)
        )
    return result.scalars().first()


async def make_consume_mark(secret: models.Secret) -> None:
    '''
    Marking secret as consumed
    '''

    async with db.async_session() as session:
        secret.consumed = True
        await session.commit()
