import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("email, password, status_code", [
    ("pes@pes.pes", "pespes", 200),
    ("pes@pes.pes", "pespes", 409),
    ("pes@pes.pes", "failedPass", 409),
    ("NotEmail", "failedPass", 422),
])
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        'auth/register',
        json={
            'email': email,
            'password': password,
        }
    )
    assert response.status_code == status_code


@pytest.mark.parametrize("email,password,status_code", [
    ("test@test.com", "test", 200),
    ("valera@example.com", "valera", 200),
    ("wrong@person.com", "valera", 401),
    ("pes@pes.pes", "pespes", 200)
])
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "auth/login",
        json={
            "email": email,
            "password": password,
        })

    assert response.status_code == status_code
