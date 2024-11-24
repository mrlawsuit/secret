
from contextlib import asynccontextmanager

from unittest.mock import patch, AsyncMock
import pytest

from app.database import init_db, dispose_engine

@asynccontextmanager
@pytest.mark.asyncio
async def test_init_db():
    async with patch('app.database.engine.begin') as mock_begin:
        mock_conn = AsyncMock()
        mock_begin.return_value.__aenter__.return_value = mock_conn

        await init_db()

        mock_begin.assert_called_once()
        mock_conn.run_sync.assert_called_once()


@asynccontextmanager
@pytest.mark.asyncio
async def test_dispose_engine():
    async with patch(
        'your_module.engine.dispose',
        new_callable=AsyncMock
    ) as mock_dispose:
        await dispose_engine()

        mock_dispose.assert_called_once()