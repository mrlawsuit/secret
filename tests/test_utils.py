from unittest.mock import patch

from app.utils import SecretManager, PasswordManager


# Tests for PasswordManager
def test_get_password_hash():
    password_mgr = PasswordManager()
    password = 'test_password'

    with patch.object(
        password_mgr.pwd_context,
        'hash',
        return_value='hashed_password'
    ) as mock_hash:
        result = password_mgr.get_password_hash(password)
        mock_hash.assert_called_once_with(password)
        assert result == 'hashed_password'


def test_verify_password_true():
    password_mgr = PasswordManager()
    password = 'test_password'
    hashed_password = 'hashed_password'

    with patch.object(
        password_mgr.pwd_context,
        'verify',
        return_value=True
    ) as mock_verify:
        result = password_mgr.verify_password(password, hashed_password)
        mock_verify.assert_called_once_with(password, hashed_password)
        assert result is True


def test_verify_password_false():
    password_mgr = PasswordManager()
    password = 'test_password'
    hashed_password = 'hashed_password'

    with patch.object(
        password_mgr.pwd_context,
        'verify',
        return_value=False
    ) as mock_verify:
        result = password_mgr.verify_password(password, hashed_password)
        mock_verify.assert_called_once_with(password, hashed_password)
        assert result is False


# Tests for SecretManager
def test_encrypt_secret():
    passphrase = 'test_passphrase'
    secret = 'test_secret'
    secret_mgr = SecretManager(passphrase)
    key = secret_mgr.key

    with patch('app.utils.Fernet') as MockFernet:
        instance = MockFernet.return_value
        instance.encrypt.return_value = b'encrypted_secret'
        result = secret_mgr.encrypt_secret(secret)
        MockFernet.assert_called_once_with(key)
        instance.encrypt.assert_called_once_with(secret.encode())
        assert result == 'encrypted_secret'


def test_decrypt_secret():
    passphrase = 'test_passphrase'
    encrypted_secret = 'encrypted_secret'
    secret_mgr = SecretManager(passphrase)
    key = secret_mgr.key

    with patch('app.utils.Fernet') as MockFernet:
        instance = MockFernet.return_value
        instance.decrypt.return_value = b'decrypted_secret'
        result = secret_mgr.decrypt_secret(encrypted_secret)
        MockFernet.assert_called_once_with(key)
        instance.decrypt.assert_called_once_with(encrypted_secret.encode())
        assert result == 'decrypted_secret'
