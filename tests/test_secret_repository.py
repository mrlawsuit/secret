import pytest
import unittest
from unittest.mock import patch, AsyncMock
from app.schemas import SecretCreate
from app.repositories.secret_repository import SecretFactory

from app import models

from datetime import datetime, timedelta, timezone
import uuid


class TestSecretFactory(unittest.TestCase):
    def test_create_success_with_ttl(self):
        with patch(
            'app.repositories.secret_repository.utils.PasswordManager'
            ) as mock_password_manager_cls, \
             patch(
                'app.repositories.secret_repository.utils.SecretManager'
            ) as mock_secret_manager_cls, \
             patch(
                'app.repositories.secret_repository.uuid.uuid4'
            ) as mock_uuid, \
             patch(
                'app.repositories.secret_repository.datetime'
            ) as mock_datetime:

            mock_uuid.side_effect = [uuid.UUID(int=1), uuid.UUID(int=0)]
            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)

            secret = SecretCreate(
                passphrase='test_passphrase',
                secret='test_secret',
                ttl=3600
            )

            mock_password_manager = mock_password_manager_cls.return_value
            mock_password_manager.get_password_hash.return_value = 'hashed_passphrase'

            mock_secret_manager = mock_secret_manager_cls.return_value
            mock_secret_manager.encrypt_secret.return_value = 'encrypted_secret'

            result = SecretFactory.create(secret)

            # Подтверждаем корректность данных вызова models.Secret
            self.assertIsInstance(result, models.Secret)
            self.assertEqual(result.id, str(uuid.UUID(int=0)))
            self.assertEqual(result.secret_key, str(uuid.UUID(int=1)))
            self.assertEqual(result.secret_data, 'encrypted_secret')
            self.assertEqual(result.passphrase_hash, 'hashed_passphrase')
            self.assertEqual(result.expires_at, mock_datetime.now() + timedelta(seconds=3600))

            # Подтверждаем корректность вызовов методов классов SecretManager, PasswordManager
            mock_password_manager.get_password_hash.assert_called_once_with('test_passphrase')
            mock_secret_manager.encrypt_secret.assert_called_once_with('test_secret')
    
    def test_create_secret_success_without_ttl(self):
        with patch(
            'app.repositories.secret_repository.utils.PasswordManager'
            ) as mock_password_manager_cls, \
             patch(
                'app.repositories.secret_repository.utils.SecretManager'
            ) as mock_secret_manager_cls, \
             patch(
                'app.repositories.secret_repository.uuid.uuid4'
            ) as mock_uuid, \
             patch(
                'app.repositories.secret_repository.datetime'
            ) as mock_datetime:
            mock_uuid.side_effect = [uuid.UUID(int=1), uuid.UUID(int=0)]
            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)

            secret = SecretCreate(
                passphrase='test_passphrase',
                secret='test_secret',
                ttl=None
            )

            mock_password_manager = mock_password_manager_cls.return_value
            mock_password_manager.get_password_hash.return_value = 'hashed_passphrase'

            mock_secret_manager = mock_secret_manager_cls.return_value
            mock_secret_manager.encrypt_secret.return_value = 'encrypted_secret'

            result = SecretFactory.create(secret)

            # Подтверждаем корректность данных вызова models.Secret
            self.assertIsInstance(result, models.Secret)
            self.assertEqual(result.id, str(uuid.UUID(int=0)))
            self.assertEqual(result.secret_key, str(uuid.UUID(int=1)))
            self.assertEqual(result.secret_data, 'encrypted_secret')
            self.assertEqual(result.passphrase_hash, 'hashed_passphrase')
            self.assertEqual(result.expires_at, None)

            # Подтверждаем корректность вызовов методов классов SecretManager, PasswordManager
            mock_password_manager.get_password_hash.assert_called_once_with('test_passphrase')
            mock_secret_manager.encrypt_secret.assert_called_once_with('test_secret')

