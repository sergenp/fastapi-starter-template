import json

import pytest
from mimesis import Address, Person
from mimesis.locales import Locale

from app.domain.users.dtos import LocationBase
from app.repositories.users.models import User, UserLocation, UserProfile

pytestmark = pytest.mark.anyio

person = Person(Locale.EN)
address = Address(Locale.EN)


async def _update_location_of_user(client, user_id: int, location: LocationBase):
    location_data = json.dumps(location.model_dump(), default=str)  # to get rid of Decimal
    location_data = json.loads(location_data)
    resp = await client.put(f"api/v1/users/{user_id}/location/", json=location_data)
    return resp


async def test_update_user_location(logged_in_client):
    longitude = address.longitude()
    latitude = address.latitude()
    location = LocationBase(longitude=longitude, latitude=latitude)
    user_id = logged_in_client.user.id
    resp = await _update_location_of_user(logged_in_client.client, user_id, location)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["latitude"] == str(latitude)
    assert data["longitude"] == str(longitude)


async def test_getting_users_within_distance(session_maker, logged_in_client):
    longitude = "50.000000"
    latitude = "50.000000"
    location = LocationBase(longitude=longitude, latitude=latitude)
    user_id = logged_in_client.user.id
    client = logged_in_client.client
    resp = await _update_location_of_user(client, user_id, location)
    assert resp.status_code == 201

    distances_within_100kms = [
        ("50.000000", "51.000000"),  # 71km / furthest
        ("50.500000", "50.200000"),  # 57 km
        ("49.500000", "50.400000"),  # 63 km
        ("49.700000", "50.123456"),  # 34 km
        ("49.900000", "50.050000"),  # 12 km / nearest
    ]

    # create users within 100 kms in distance to logged_in_client
    async with session_maker() as session:
        for lat, lon in distances_within_100kms:
            username = person.username()
            email = person.email()
            password = person.password()
            is_active = True
            user = User(username=username, email=email, password=password, is_active=is_active)
            latitude = lat
            longitude = lon
            user.location = UserLocation(latitude=latitude, longitude=longitude)
            user.profile = UserProfile()
            session.add(user)
        await session.commit()

    resp = await client.get("api/v1/users/?distance=100")
    assert resp.json()["total"] == 5

    resp = await client.get("api/v1/users/?distance=50")
    assert resp.json()["total"] == 2
    # results are sorted by distance, so, first result is the nearest on (about 12 kms)
    nearest = resp.json()["results"][0]["distance"]
    assert round(nearest - 11.68, 2) == 0

    second_nearest = resp.json()["results"][1]["distance"]
    assert round(second_nearest - 34.51, 2) == 0

    resp = await client.get("api/v1/users/?distance=5")
    assert resp.json()["total"] == 0
