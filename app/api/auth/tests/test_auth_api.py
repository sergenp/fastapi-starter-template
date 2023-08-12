import pytest
from mimesis import Person

from app.domain.auth.dtos import RegisterPayload

pytestmark = pytest.mark.anyio
person = Person()


async def test_login_fail(client):
    response = await client.post("api/v1/login/", json={"username": "foo", "password": "bar"})
    assert response.status_code == 401


async def test_login_success(client):
    data = RegisterPayload(email="foo@mail.com", password="bar", username="example_username")
    response = await client.post("api/v1/register/", json=data.model_dump())
    response = await client.post(
        "api/v1/login/",
        json={
            "email": "foo@mail.com",
            "password": "bar",
            "username": "example_username",
        },
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    response = await client.get("api/v1/me/", headers={"Authorization": f"Bearer {access_token}"})
    # since we didn't confirm with email,
    # we shouldn't be able to access any other endpoint that needs a user
    assert response.status_code == 401


async def test_refresh_token(logged_in_client):
    user = logged_in_client.user
    client = logged_in_client.client

    response = await client.post(
        "api/v1/refresh-token/", json={"refresh_token": f"{user.refresh_token}"}
    )
    response = response.json()
    assert response["access_token"] != user.access_token
    assert response["refresh_token"] == user.refresh_token


async def test_register(client):
    user_data = RegisterPayload(
        email=person.email(),
        password=person.password(),
        username=person.username(),
    )
    response = await client.post("api/v1/register/", json=user_data.model_dump())
    response = response.json()
    assert response.get("access_token") is not None
    assert response.get("refresh_token") is not None
