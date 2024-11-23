import hashlib
import base64
from cryptography.fernet import Fernet
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'])


def get_password_hash(password: str) -> str:
    '''function for hashing pasword'''
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    '''Compares password and hash'''
    return pwd_context.verify(password, hashed_password)


def get_key(passphrase: str) -> bytes:
    '''get the encryption key from passphrase'''
    sha = hashlib.sha256()
    sha.update(passphrase.encode())
    return base64.urlsafe_b64encode(sha.digest())


def encrypt_secret(secret: str, passphrase: str) -> str:
    '''Encrypt the secret using the passphrase'''

    key = get_key(passphrase)
    f = Fernet(key)
    return f.encrypt(secret.encode()).decode()


def decrypt_seceret(encrypted_secret: str, passphrase: str) -> str:
    '''Decrypt the secret using the passphrase'''
    key = get_key(passphrase)
    f = Fernet(key)
    return f.decrypt(encrypted_secret.encode()).decode()

