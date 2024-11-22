from database import async_session

import schemas as shm


async def create_secret(secret: shm.SecretCreate) -> str:
    pass