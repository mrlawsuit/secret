import uuid
from datetime import datetime, timedelta, timezone, UTC
from contextlib import asynccontextmanager

import pytest
import unittest
from unittest.mock import patch, AsyncMock

from app import models
from app.schemas import SecretCreate
from app.repositories.secret_repository import SecretFactory, create_secret


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


@asynccontextmanager
@pytest.mark.asyncio
async def test_cretate_secret_with_ttl():
    with patch.object(SecretFactory, 'create', return_value=models.Secret(
        id='mock_id',
        secret_key='mock_key',
        secret_data='mock_secret_data',
        passphrase_hash='mock_passphrase_hash',
        expires_at=datetime.now(UTC) + timedelta(seconds=3600)
    )) as mock_create, \
    patch(
        'app.repositories.secret_repository.db.async_session',
        new_callable=AsyncMock
    ) as mock_session:

        # Создаем экземпляр секрета
        secret_create = SecretCreate(
            passphrase='test_passphrase',
            secret='test_secret',
            ttl=3600
        )

        # Вызов тестируемого кода
        mock_session_instance = (
            mock_session.return_value.__aenter__.return_value
        )
        secret_key = await create_secret(secret_create)

        # Проверка вызова фабрики SecretFactory.create
        mock_create.assert_called_once_with(secret_create)

        # Проверка, что объект был добавлен в сессию
        mock_session_instance.add.assert_called_once()
        added_secret = mock_session_instance.add.call_args[0][0]
        assert added_secret.secret_key == 'mock_key'

        # Проверка коммита
        mock_session_instance.commit.assert_awaited_once()

        # Проверка возвращённого значения
        assert secret_key == 'mock_key'


@asynccontextmanager
@pytest.mark.asyncio
async def test_cretate_secret_without_ttl():
    with patch.object(SecretFactory, 'create', return_value=models.Secret(
        id='mock_id',
        secret_key='mock_key',
        secret_data='mock_secret_data',
        passphrase_hash='mock_passphrase_hash',
        expires_at=datetime.now(UTC) + timedelta(seconds=3600)
    )) as mock_create, \
    patch(
        'app.repositories.secret_repository.db.async_session',
        new_callable=AsyncMock
    ) as mock_session:

        # Создаем экземпляр секрета
        secret_create = SecretCreate(
            passphrase='test_passphrase',
            secret='test_secret',
            ttl=None
        )

        # Вызов тестируемого кода
        mock_session_instance = (
            mock_session.return_value.__aenter__.return_value
        )
        secret_key = await create_secret(secret_create)

        # Проверка вызова фабрики SecretFactory.create
        mock_create.assert_called_once_with(secret_create)

        # Проверка, что объект был добавлен в сессию
        mock_session_instance.add.assert_called_once()
        added_secret = mock_session_instance.add.call_args[0][0]
        assert added_secret.secret_key == 'mock_key'

        # Проверка отсутствия expires_at
        assert added_secret.expires_at is None

        # Проверка коммита
        mock_session_instance.commit.assert_awaited_once()

        # Проверка возвращённого значения
        assert secret_key == 'mock_key'

