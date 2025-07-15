"""Test configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI

from app.main import app
from app.core.database import Base, get_db
from app.models import User, Achievement, UserAchievement


# Test database URL - using SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with in-memory SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database and return session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    """Create test client with test database."""
    
    async def override_get_db():
        """Override database dependency for testing."""
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_user(test_db: AsyncSession):
    """Create a sample user for testing."""
    user = User(username="testuser", language="ru")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_achievement(test_db: AsyncSession):
    """Create a sample achievement for testing."""
    achievement = Achievement(
        name_ru="Первые шаги",
        name_en="First Steps",
        description_ru="Ваше первое достижение",
        description_en="Your first achievement",
        points=10
    )
    test_db.add(achievement)
    await test_db.commit()
    await test_db.refresh(achievement)
    return achievement


@pytest_asyncio.fixture
async def multiple_users(test_db: AsyncSession):
    """Create multiple users for complex testing."""
    users = [
        User(username="user1", language="ru"),
        User(username="user2", language="en"),
        User(username="user3", language="ru"),
        User(username="user4", language="en"),
        User(username="user5", language="ru"),
    ]
    
    for user in users:
        test_db.add(user)
    
    await test_db.commit()
    
    for user in users:
        await test_db.refresh(user)
    
    return users


@pytest_asyncio.fixture
async def multiple_achievements(test_db: AsyncSession):
    """Create multiple achievements for complex testing."""
    achievements = [
        Achievement(
            name_ru="Новичок",
            name_en="Beginner",
            description_ru="Первые шаги в системе",
            description_en="First steps in the system",
            points=5
        ),
        Achievement(
            name_ru="Исследователь",
            name_en="Explorer",
            description_ru="Изучение возможностей",
            description_en="Exploring capabilities",
            points=15
        ),
        Achievement(
            name_ru="Эксперт",
            name_en="Expert",
            description_ru="Мастерство в использовании",
            description_en="Mastery in usage",
            points=30
        ),
        Achievement(
            name_ru="Чемпион",
            name_en="Champion",
            description_ru="Высший уровень мастерства",
            description_en="Highest level of mastery",
            points=50
        ),
        Achievement(
            name_ru="Легенда",
            name_en="Legend",
            description_ru="Легендарный статус",
            description_en="Legendary status",
            points=100
        ),
    ]
    
    for achievement in achievements:
        test_db.add(achievement)
    
    await test_db.commit()
    
    for achievement in achievements:
        await test_db.refresh(achievement)
    
    return achievements


@pytest_asyncio.fixture
async def populated_database(test_db: AsyncSession, multiple_users, multiple_achievements):
    """Create a populated database for complex statistics testing."""
    users = multiple_users
    achievements = multiple_achievements
    
    # Create various user-achievement relationships for testing
    user_achievements = []
    
    # User 1: Gets achievements 1, 2, 3 (total: 50 points, 3 achievements)
    for i in range(3):
        ua = UserAchievement(user_id=users[0].id, achievement_id=achievements[i].id)
        user_achievements.append(ua)
    
    # User 2: Gets achievements 1, 2, 3, 4 (total: 100 points, 4 achievements)
    for i in range(4):
        ua = UserAchievement(user_id=users[1].id, achievement_id=achievements[i].id)
        user_achievements.append(ua)
    
    # User 3: Gets only achievement 5 (total: 100 points, 1 achievement)
    ua = UserAchievement(user_id=users[2].id, achievement_id=achievements[4].id)
    user_achievements.append(ua)
    
    # User 4: Gets achievements 1, 2 (total: 20 points, 2 achievements)
    for i in range(2):
        ua = UserAchievement(user_id=users[3].id, achievement_id=achievements[i].id)
        user_achievements.append(ua)
    
    # User 5: No achievements (total: 0 points, 0 achievements)
    
    for ua in user_achievements:
        test_db.add(ua)
    
    await test_db.commit()
    
    return {
        "users": users,
        "achievements": achievements,
        "user_achievements": user_achievements
    }