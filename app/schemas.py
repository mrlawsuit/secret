from typing import Optional

from pydantic import BaseModel, Field


class SecretBase(BaseModel):
    '''Base schema for secret requests'''

    secret: str
    passphrase: str
    ttl: Optional[int] = Field(
        None, description='Time to live in seconds for secret'
    )


class SecretCreate(SecretBase):
    '''Schema for creating secrets'''


class SecretKeyResponse(BaseModel):
    '''Recponse schema containing the generated secret key'''
    secret_key: str


class SecretResponse(BaseModel):
    '''Response schema containing the dewcrypted secret'''

    secret: str
