import hashlib
import base64
from cryptography.fernet import Fernet
from passlib.context import CryptContext


class PasswordManager:
    '''
    Class for managing hash and password check
    '''

    def __init__(self, schemes=['bcrypt']):
        self.pwd_context = CryptContext(schemes=schemes)

    def get_password_hash(self, password: str) -> str:
        '''method for hashing pasword'''
        return self.pwd_context.hash(password)

    def verify_password(
            self,
            password: str,
            hashed_password: str
    ) -> bool:
        '''
        Compares password and hash
        '''

        return self.pwd_context.verify(password, hashed_password)


class SecretManager:
    def __init__(self, passphrase: str) -> None:
        self.passphrase = passphrase
        self.key = self._get_key(passphrase)

    @staticmethod
    def _get_key(passphrase: str) -> bytes:
        '''
        get the encryption key from passphrase
        '''

        sha = hashlib.sha256()
        sha.update(passphrase.encode())
        return base64.urlsafe_b64encode(sha.digest())

    def encrypt_secret(self, secret: str) -> str:
        '''
        Encrypt the secret using the passphrase
        '''

        f = Fernet(self.key)
        return f.encrypt(secret.encode()).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        '''
        Decrypt the secret using the passphrase
        '''

        f = Fernet(self.key)
        return f.decrypt(encrypted_secret.encode()).decode()
