"""Tests for achievement endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Achievement


class TestAchievementEndpoints:
    """Test class for achievement-related endpoints."""

    @pytest.mark.asyncio
    async def test_create_achievement(self, client: AsyncClient):
        """Test creating a new achievement."""
        achievement_data = {
            "name_ru": "Тестовое достижение",
            "name_en": "Test Achievement",
            "description_ru": "Описание тестового достижения",
            "description_en": "Test achievement description",
            "points": 25
        }
        
        response = await client.post("/achievements/", json=achievement_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name_ru"] == "Тестовое достижение"
        assert data["name_en"] == "Test Achievement"
        assert data["description_ru"] == "Описание тестового достижения"
        assert data["description_en"] == "Test achievement description"
        assert data["points"] == 25
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_achievement_invalid_points(self, client: AsyncClient):
        """Test creating achievement with invalid points."""
        achievement_data = {
            "name_ru": "Тестовое достижение",
            "name_en": "Test Achievement",
            "description_ru": "Описание тестового достижения",
            "description_en": "Test achievement description",
            "points": -5  # Invalid negative points
        }
        
        response = await client.post("/achievements/", json=achievement_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_achievement_by_id(self, client: AsyncClient, sample_achievement: Achievement):
        """Test getting achievement by ID."""
        response = await client.get(f"/achievements/{sample_achievement.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_achievement.id
        assert data["name_ru"] == sample_achievement.name_ru
        assert data["name_en"] == sample_achievement.name_en
        assert data["description_ru"] == sample_achievement.description_ru
        assert data["description_en"] == sample_achievement.description_en
        assert data["points"] == sample_achievement.points

    @pytest.mark.asyncio
    async def test_get_achievement_not_found(self, client: AsyncClient):
        """Test getting non-existent achievement returns 404."""
        response = await client.get("/achievements/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Achievement not found"

    @pytest.mark.asyncio
    async def test_get_all_achievements(self, client: AsyncClient, multiple_achievements):
        """Test getting all achievements."""
        response = await client.get("/achievements/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # multiple_achievements fixture creates 5 achievements
        
        # Check that all achievements are returned
        names_ru = [achievement["name_ru"] for achievement in data]
        expected_names = ["Новичок", "Исследователь", "Эксперт", "Чемпион", "Легенда"]
        assert all(name in names_ru for name in expected_names)

    @pytest.mark.asyncio
    async def test_get_all_achievements_with_pagination(self, client: AsyncClient, multiple_achievements):
        """Test getting achievements with pagination."""
        response = await client.get("/achievements/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limit is 2

    @pytest.mark.asyncio
    async def test_award_achievement_success(self, client: AsyncClient, sample_user: User, sample_achievement: Achievement):
        """Test successfully awarding achievement to user."""
        award_data = {
            "user_id": sample_user.id,
            "achievement_id": sample_achievement.id
        }
        
        response = await client.post("/achievements/award", json=award_data)
        
        assert response.status_code == 201
        
        # Verify the award was created by checking user's achievements
        user_achievements_response = await client.get(f"/users/{sample_user.id}/achievements")
        assert user_achievements_response.status_code == 200
        achievements = user_achievements_response.json()
        assert len(achievements) == 1
        assert achievements[0]["id"] == sample_achievement.id

    @pytest.mark.asyncio
    async def test_award_achievement_user_not_found(self, client: AsyncClient, sample_achievement: Achievement):
        """Test awarding achievement to non-existent user."""
        award_data = {
            "user_id": 999,  # Non-existent user
            "achievement_id": sample_achievement.id
        }
        
        response = await client.post("/achievements/award", json=award_data)
        
        assert response.status_code == 400  # Should handle user not found error

    @pytest.mark.asyncio
    async def test_award_achievement_achievement_not_found(self, client: AsyncClient, sample_user: User):
        """Test awarding non-existent achievement to user."""
        award_data = {
            "user_id": sample_user.id,
            "achievement_id": 999  # Non-existent achievement
        }
        
        response = await client.post("/achievements/award", json=award_data)
        
        assert response.status_code == 400  # Should handle achievement not found error

    @pytest.mark.asyncio
    async def test_award_achievement_duplicate(self, client: AsyncClient, sample_user: User, sample_achievement: Achievement):
        """Test awarding the same achievement twice fails."""
        award_data = {
            "user_id": sample_user.id,
            "achievement_id": sample_achievement.id
        }
        
        # First award should succeed
        response1 = await client.post("/achievements/award", json=award_data)
        assert response1.status_code == 201
        
        # Second award should fail
        response2 = await client.post("/achievements/award", json=award_data)
        assert response2.status_code == 400  # Should handle duplicate award error

    @pytest.mark.asyncio
    async def test_award_multiple_achievements_to_user(self, client: AsyncClient, sample_user: User, multiple_achievements):
        """Test awarding multiple achievements to the same user."""
        achievements = multiple_achievements[:3]  # Take first 3 achievements
        
        # Award each achievement
        for achievement in achievements:
            award_data = {
                "user_id": sample_user.id,
                "achievement_id": achievement.id
            }
            response = await client.post("/achievements/award", json=award_data)
            assert response.status_code == 201
        
        # Verify all achievements were awarded
        user_achievements_response = await client.get(f"/users/{sample_user.id}/achievements")
        assert user_achievements_response.status_code == 200
        user_achievements = user_achievements_response.json()
        assert len(user_achievements) == 3
        
        # Check that all expected achievements are present
        awarded_ids = [ua["id"] for ua in user_achievements]
        expected_ids = [achievement.id for achievement in achievements]
        assert set(awarded_ids) == set(expected_ids)

    @pytest.mark.asyncio
    async def test_award_achievement_missing_fields(self, client: AsyncClient):
        """Test awarding achievement with missing required fields."""
        award_data = {
            "user_id": 1
            # Missing achievement_id
        }
        
        response = await client.post("/achievements/award", json=award_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_achievement_missing_fields(self, client: AsyncClient):
        """Test creating achievement with missing required fields."""
        achievement_data = {
            "name_ru": "Тестовое достижение",
            "name_en": "Test Achievement",
            # Missing description fields and points
        }
        
        response = await client.post("/achievements/", json=achievement_data)
        
        assert response.status_code == 422  # Validation error