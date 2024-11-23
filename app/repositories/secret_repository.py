from datetime import datetime, timedelta, UTC
import uuid

from app import database as db
import app.schemas as shm
import app.utils as utils
from app import models


async def create_secret(secret: shm.SecretCreate) -> str:
    '''create record in db with new secret'''
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
