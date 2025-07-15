"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class TestUserEndpoints:
    """Test class for user-related endpoints."""

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """Test creating a new user."""
        user_data = {
            "username": "newuser",
            "language": "ru"
        }
        
        response = await client.post("/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["language"] == "ru"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, client: AsyncClient, sample_user: User):
        """Test creating a user with duplicate username fails."""
        user_data = {
            "username": sample_user.username,
            "language": "en"
        }
        
        response = await client.post("/users/", json=user_data)
        
        assert response.status_code == 400  # Should handle duplicate username error

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, sample_user: User):
        """Test getting user by ID."""
        response = await client.get(f"/users/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["language"] == sample_user.language

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Test getting non-existent user returns 404."""
        response = await client.get("/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_all_users(self, client: AsyncClient, multiple_users):
        """Test getting all users."""
        response = await client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # multiple_users fixture creates 5 users
        
        # Check that all users are returned
        usernames = [user["username"] for user in data]
        expected_usernames = ["user1", "user2", "user3", "user4", "user5"]
        assert all(username in usernames for username in expected_usernames)

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, client: AsyncClient, multiple_users):
        """Test getting users with pagination."""
        response = await client.get("/users/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limit is 2

    @pytest.mark.asyncio
    async def test_get_user_achievements_empty(self, client: AsyncClient, sample_user: User):
        """Test getting achievements for user with no achievements."""
        response = await client.get(f"/users/{sample_user.id}/achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_user_achievements_with_data(self, client: AsyncClient, test_db: AsyncSession, sample_user: User, sample_achievement):
        """Test getting achievements for user with achievements."""
        # First, award the achievement to the user
        award_data = {
            "user_id": sample_user.id,
            "achievement_id": sample_achievement.id
        }
        await client.post("/achievements/award", json=award_data)
        
        # Then get user's achievements
        response = await client.get(f"/users/{sample_user.id}/achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        achievement = data[0]
        assert achievement["id"] == sample_achievement.id
        assert achievement["points"] == sample_achievement.points
        
        # Check localization - user has 'ru' language
        assert achievement["name"] == sample_achievement.name_ru
        assert achievement["description"] == sample_achievement.description_ru

    @pytest.mark.asyncio
    async def test_get_user_achievements_localization_en(self, client: AsyncClient, test_db: AsyncSession, sample_achievement):
        """Test achievements localization for English user."""
        # Create English user
        user_data = {
            "username": "englishuser",
            "language": "en"
        }
        user_response = await client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]
        
        # Award achievement to user
        award_data = {
            "user_id": user_id,
            "achievement_id": sample_achievement.id
        }
        await client.post("/achievements/award", json=award_data)
        
        # Get user's achievements
        response = await client.get(f"/users/{user_id}/achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        achievement = data[0]
        # Check English localization
        assert achievement["name"] == sample_achievement.name_en
        assert achievement["description"] == sample_achievement.description_en

    @pytest.mark.asyncio
    async def test_get_user_achievements_not_found(self, client: AsyncClient):
        """Test getting achievements for non-existent user."""
        response = await client.get("/users/999/achievements")
        
        assert response.status_code == 404  # Should handle user not found error

    @pytest.mark.asyncio
    async def test_create_user_invalid_language(self, client: AsyncClient):
        """Test creating user with invalid language."""
        user_data = {
            "username": "testuser",
            "language": "invalid"
        }
        
        response = await client.post("/users/", json=user_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_user_with_default_language(self, client: AsyncClient):
        """Test creating user with missing language field sets default language."""
        user_data = {
            "username": "default_lang_user"
            # Missing language field
        }
        
        response = await client.post("/users/", json=user_data)
        
        assert response.status_code == 201  # Should be successfully created
        response_json = response.json()
        assert response_json["username"] == "default_lang_user"
        assert "language" in response_json
        assert response_json["language"] == "ru"  # Проверяем язык по умолчанию