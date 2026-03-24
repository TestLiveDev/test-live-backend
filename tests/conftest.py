import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base, Project, ProjectMember, ProjectRole, User
from app.security import get_current_user, get_password_hash

TEST_DATABASE_URL = (
    "postgresql+asyncpg://devuser:devpassword@localhost:5432/test_live_mvp_test"
)


@pytest_asyncio.fixture
async def db_session():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_session_local = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_local() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def seed_user(db_session):
    seeded_user = User(
        email="owner@example.com",
        password_hash=get_password_hash("password123"),
        full_name="Owner User",
    )
    db_session.add(seeded_user)
    await db_session.commit()
    await db_session.refresh(seeded_user)
    return seeded_user


@pytest_asyncio.fixture
async def client(db_session, seed_user):

    async def override_get_db():
        yield db_session

    async def override_current_user():
        return seed_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_project(db_session, seed_user):
    project = Project(name="Default Project")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    membership = ProjectMember(
        id_project=project.id,
        id_user=seed_user.id,
        role=ProjectRole.OWNER.value,
    )
    db_session.add(membership)
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def raw_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_for_user(db_session):
    async def _build_client(user):
        async def override_get_db():
            yield db_session

        async def override_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_current_user

        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    try:
        yield _build_client
    finally:
        app.dependency_overrides.clear()
