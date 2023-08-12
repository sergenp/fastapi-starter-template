import contextlib
import dataclasses
from pathlib import Path

import pytest
import sqlalchemy
import sqlalchemy.exc
from httpx import AsyncClient
from mimesis import Locale, Person
from passlib.hash import pbkdf2_sha256
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from app.config import settings
from app.infrastructure.services.minio_service import MinioService
from app.infrastructure.services.session_service import SessionMaker
from app.main import app
from app.repositories.users.models import User, UserProfile

person = Person(Locale.EN)

settings.EMAIL_SUPRESS_SEND = True


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


engine = create_async_engine(
    settings.TEST_DATABASE_URI.unicode_string(), echo=False, poolclass=NullPool
)

async_session_maker: AsyncSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture()
async def session_maker():
    connection = await engine.connect()
    transaction = await connection.begin()

    class TestSessionMaker:
        async def __aenter__(self) -> AsyncSession:
            self.session = async_session_maker(bind=connection)
            return self.session

        async def __aexit__(self, *args, **kwargs):
            await self.session.close()

    yield TestSessionMaker

    # roll everything back
    await transaction.rollback()
    await connection.close()


@pytest.fixture()
async def minio_service(scope="session"):
    class TestMinioService(MinioService):
        def __init__(self) -> None:
            super().__init__()
            self.bucket_name = "test-bucket"
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)

    yield TestMinioService

    # after using the service, delete all objects in the bucket
    # so that the bucket can be deleted,
    # just basic tear down after tests
    service = TestMinioService()
    objects = service.client.list_objects(service.bucket_name, recursive=True)
    service.client.remove_objects(service.bucket_name, objects)
    service.client.remove_bucket(service.bucket_name)


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        # postgresql+asyncpg://postgres:postgres@localhost/apitestdb
        async with create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost/postgres",
            isolation_level="AUTOCOMMIT",
        ).connect() as connection:
            await connection.execute(
                text(f"CREATE DATABASE {settings.TEST_DATABASE_URI.path.replace('/','')}")
            )


@pytest.fixture(scope="session", autouse=True)
def create_db_tables(create_test_db) -> None:
    # retrieves the directory that *this* file is in
    migrations_dir = str(Path(__file__).parent.resolve() / "alembic")
    # this assumes the alembic.ini is also contained in this same directory
    config_file = str(Path(__file__).parent.resolve() / "alembic.ini")

    config = Config(file_=config_file)
    config.set_main_option("script_location", migrations_dir)
    config.set_main_option("sqlalchemy.url", settings.TEST_DATABASE_URI.unicode_string())
    # upgrade the database to the latest revision
    command.upgrade(config, "head")


@pytest.fixture()
async def client(session_maker, minio_service):
    app.dependency_overrides[SessionMaker] = session_maker
    app.dependency_overrides[MinioService] = minio_service

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    del app.dependency_overrides[SessionMaker]
    del app.dependency_overrides[MinioService]


@dataclasses.dataclass
class ApiUser:
    id: int
    username: str
    email: str
    password: str
    access_token: str
    refresh_token: str


@dataclasses.dataclass
class LoggedInClient:
    client: AsyncClient
    user: User


@pytest.fixture()
async def logged_in_client(session_maker, client):
    """
    Returns a LoggedInClient instance with access_token and refresh_token,
    AsyncClient instance with Authorization header set, and user's email
    """
    async with session_maker() as session:
        username = person.username()
        email = person.email()
        password = person.password()
        hashed_password = pbkdf2_sha256.hash(password)
        is_active = True
        user = User(username=username, email=email, password=hashed_password, is_active=is_active)
        user.profile = UserProfile()
        session.add(user)
        await session.commit()

    resp = await client.post("api/v1/login/", json={"username": username, "password": password})
    assert resp.status_code == 200

    tokens = resp.json()

    user = ApiUser(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        id=user.id,
        username=username,
        email=email,
        password=password,
    )
    client.headers = {"Authorization": f"Bearer {user.access_token}"}
    client = LoggedInClient(client=client, user=user)

    yield client
