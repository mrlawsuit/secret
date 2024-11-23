import uuid

from app import database as db
import app.schemas as shm


async def create_secret(secret: shm.SecretCreate) -> str:
    '''create record in db with new secret'''
    pass


