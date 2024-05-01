import asyncio
import json
from datetime import datetime
from functools import wraps
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.bookings.models import Bookings
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users


# We need to disable the @cache decorator during testing
def mock_cache(*args, **kwargs):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)

        return inner

    return wrapper


mock.patch("fastapi_cache.decorator.cache", mock_cache).start()

# В связи с отключением кэша и функции выше, импортировать приложение fastapi нужно после
from app.main import app as fastapi_app


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="UTF-8") as file:
            return json.load(file)

    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")

    for booking in bookings:
        # SQLAlchemy не принимает дату в текстовом формате, поэтому форматируем к datetime
        booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d")
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d")

    async with async_session_maker() as session:
        for Model, values in [
            (Hotels, hotels),
            (Rooms, rooms),
            (Users, users),
            (Bookings, bookings),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)
        await session.commit()


# Взято из документации к pytest-asyncio
# Создаем новый event loop для прогона тестов
# №2  pytest ругается ( DeprecationWarning: The event_loop fixture provided by pytest-asyncio
# has been redefined in.." и говорит используй scope="session"
# @pytest.fixture(scope="session")
# def event_loop(request):
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="function")
async def ac():
    "Асинхронный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    "Асинхронный аутентифицированный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        await ac.post(
            "auth/login",
            json={
                "email": "test@test.com",
                "password": "test",
            },
        )
        assert ac.cookies["booking_access_token"]
        yield ac
