import pytest
from mimesis import Person
from mimesis.locales import Locale

from app.domain.auth.dtos import RegisterPayload

pytestmark = pytest.mark.anyio

person = Person(Locale.EN)


async def _create_user(client, user_data: RegisterPayload):
    resp = await client.post("api/v1/register/", json=user_data.model_dump())
    return resp


async def test_creating_user_with_existing_email(client):
    """Test creating user with email that already exists"""
    user_data = RegisterPayload(
        email=person.email(),
        password=person.password(),
        username=person.username(),
    )

    resp = await _create_user(client, user_data)

    assert resp.status_code == 201

    resp = await _create_user(client, user_data)
    assert resp.status_code == 400


async def test_getting_users(logged_in_client):
    client = logged_in_client.client

    resp = await client.get("api/v1/me/")
    user_id = resp.json()["id"]

    resp = await client.get(f"api/v1/users/{user_id}/")
    assert resp.status_code == 200


async def test_update_user_profile(logged_in_client):
    first_name = person.first_name()
    last_name = person.last_name()
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "birthday": "1990-01-01",
    }
    resp = await logged_in_client.client.put("api/v1/users/me/profile/", json=payload)
    assert resp.status_code == 201

    resp = await logged_in_client.client.get("api/v1/me/")
    resp = resp.json()

    assert resp["profile"]["first_name"] == first_name
    assert resp["profile"]["last_name"] == last_name
    assert resp["profile"]["birthday"] == "1990-01-01"


async def test_update_user_profile_forbidden(client):
    first_name = person.first_name()
    last_name = person.last_name()
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "birthday": "1990-01-01",
    }
    resp = await client.put("api/v1/users/me/profile/", json=payload)
    # client isn't authenticated
    assert resp.status_code == 403
