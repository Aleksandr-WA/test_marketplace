import asyncio
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import pytest
from app.core.config import settings
from app.core.db_helper import DatabaseHelper, db_helper
from app.main import main_app
from app.models.base import Base
from fastapi.testclient import TestClient


DATABASE_URL_TEST = URL_DATABASE_ASYNC = (
    f"{settings.db_test.dialect}+"
    f"{settings.db_test.driver_async}://"
    f"{settings.db_test.user}:"
    f"{settings.db_test.password}@"
    f"{settings.db_test.host}:"
    f"{settings.db_test.port}/"
    f"{settings.db_test.database}"
)


db_helper_test = DatabaseHelper(
    url=DATABASE_URL_TEST,
    echo=settings.db_test.echo,
    echo_pool=settings.db_test.echo_pool,
    pool_size=settings.db_test.pool_size,
    max_overflow=settings.db_test.max_overflow,
)

Base.metadata.bind = db_helper_test.engine

main_app.dependency_overrides[db_helper.session_getter] = db_helper_test.session_getter

client = TestClient(main_app)


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with db_helper_test.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_helper_test.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as async_client:
        yield async_client


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
