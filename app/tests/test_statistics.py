"""Tests for statistics endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models import User, Achievement, UserAchievement


class TestStatisticsEndpoints:
    """Test class for statistics-related endpoints."""

    @pytest.mark.asyncio
    async def test_top_by_achievements_with_data(self, client: AsyncClient, populated_database):
        """Test getting user with most achievements."""
        response = await client.get("/stats/top-by-achievements")
        
        assert response.status_code == 200
        data = response.json()
        
        # User 2 has 4 achievements (most)
        assert data["user_id"] == populated_database["users"][1].id
        assert data["username"] == "user2"
        assert data["achievement_count"] == 4

    @pytest.mark.asyncio
    async def test_top_by_achievements_no_data(self, client: AsyncClient, multiple_users):
        """Test getting user with most achievements when no achievements exist."""
        response = await client.get("/stats/top-by-achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No users with achievements found"

    @pytest.mark.asyncio
    async def test_top_by_points_with_data(self, client: AsyncClient, populated_database):
        """Test getting user with most points."""
        response = await client.get("/stats/top-by-points")
        
        assert response.status_code == 200
        data = response.json()
        
        # Both user2 and user3 have 100 points, but user2 should be first
        assert data["user_id"] in [populated_database["users"][1].id, populated_database["users"][2].id]
        assert data["total_points"] == 100

    @pytest.mark.asyncio
    async def test_top_by_points_no_data(self, client: AsyncClient, multiple_users):
        """Test getting user with most points when no achievements exist."""
        response = await client.get("/stats/top-by-points")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No users with achievements found"

    @pytest.mark.asyncio
    async def test_min_max_points_difference(self, client: AsyncClient, populated_database):
        """Test getting min and max points difference."""
        response = await client.get("/stats/min-max-points-difference")
        
        assert response.status_code == 200
        data = response.json()
        
        # User5 has 0 points (min), User2 or User3 have 100 points (max)
        assert data["min_points_user"]["total_points"] == 0
        assert data["min_points_user"]["username"] == "user5"
        assert data["max_points_user"]["total_points"] == 100
        assert data["max_points_user"]["username"] in ["user2", "user3"]
        assert data["points_difference"] == 100

    @pytest.mark.asyncio
    async def test_min_max_points_difference_insufficient_users(self, client: AsyncClient, sample_user):
        """Test getting min max points difference with insufficient users."""
        response = await client.get("/stats/min-max-points-difference")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not enough users to calculate difference"

    @pytest.mark.asyncio
    async def test_7_day_streak_users_no_data(self, client: AsyncClient, multiple_users):
        """Test getting 7-day streak users with no data."""
        response = await client.get("/stats/7-day-streak-users")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_7_day_streak_users_with_streak(self, client: AsyncClient, test_db: AsyncSession):
        """Test getting 7-day streak users with actual streak data."""
        # Create user and achievements
        user = User(username="streak_user", language="ru")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        achievement = Achievement(
            name_ru="Ежедневное достижение",
            name_en="Daily Achievement",
            description_ru="Получается каждый день",
            description_en="Earned daily",
            points=1
        )
        test_db.add(achievement)
        await test_db.commit()
        await test_db.refresh(achievement)
        
        # Create 7 consecutive days of achievements
        base_date = datetime.now() - timedelta(days=10)
        for i in range(7):
            award_date = base_date + timedelta(days=i)
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                awarded_at=award_date
            )
            test_db.add(user_achievement)
        
        await test_db.commit()
        
        response = await client.get("/stats/7-day-streak-users")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return the user with 7-day streak
        assert len(data) == 1
        assert data[0]["user_id"] == user.id
        assert data[0]["username"] == "streak_user"
        assert data[0]["consecutive_days"] == 7

    @pytest.mark.asyncio
    async def test_complex_statistics_scenario(self, client: AsyncClient, test_db: AsyncSession):
        """Test complex statistics scenario with multiple users and achievements."""
        # Create users
        users = []
        for i in range(1, 6):
            user = User(username=f"complex_user_{i}", language="ru")
            test_db.add(user)
            users.append(user)
        
        # Create achievements with varying points
        achievements = []
        points_list = [1, 5, 10, 25, 50]
        for i, points in enumerate(points_list):
            achievement = Achievement(
                name_ru=f"Достижение {i+1}",
                name_en=f"Achievement {i+1}",
                description_ru=f"Описание {i+1}",
                description_en=f"Description {i+1}",
                points=points
            )
            test_db.add(achievement)
            achievements.append(achievement)
        
        await test_db.commit()
        
        # Refresh all objects
        for user in users:
            await test_db.refresh(user)
        for achievement in achievements:
            await test_db.refresh(achievement)
        
        # Create strategic achievement awards
        # User 1: Gets all achievements (total: 91 points, 5 achievements)
        # User 2: Gets achievements 1,2,3 (total: 16 points, 3 achievements)
        # User 3: Gets achievement 5 only (total: 50 points, 1 achievement)
        # User 4: Gets achievements 1,2 (total: 6 points, 2 achievements)
        # User 5: No achievements (total: 0 points, 0 achievements)
        
        award_patterns = [
            (0, [0, 1, 2, 3, 4]),  # User 1 gets all
            (1, [0, 1, 2]),        # User 2 gets first 3
            (2, [4]),              # User 3 gets last one
            (3, [0, 1]),           # User 4 gets first 2
            (4, [])                # User 5 gets none
        ]
        
        for user_idx, achievement_indices in award_patterns:
            for achievement_idx in achievement_indices:
                user_achievement = UserAchievement(
                    user_id=users[user_idx].id,
                    achievement_id=achievements[achievement_idx].id
                )
                test_db.add(user_achievement)
        
        await test_db.commit()
        
        # Test top by achievements
        response = await client.get("/stats/top-by-achievements")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == users[0].id  # User 1 has most achievements (5)
        assert data["achievement_count"] == 5
        
        # Test top by points
        response = await client.get("/stats/top-by-points")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == users[0].id  # User 1 has most points (91)
        assert data["total_points"] == 91
        
        # Test min/max points difference
        response = await client.get("/stats/min-max-points-difference")
        assert response.status_code == 200
        data = response.json()
        assert data["min_points_user"]["user_id"] == users[4].id  # User 5 has 0 points
        assert data["min_points_user"]["total_points"] == 0
        assert data["max_points_user"]["user_id"] == users[0].id  # User 1 has 91 points
        assert data["max_points_user"]["total_points"] == 91
        assert data["points_difference"] == 91

    @pytest.mark.asyncio
    async def test_multiple_users_same_achievement_count(self, client: AsyncClient, test_db: AsyncSession):
        """Test statistics when multiple users have same achievement count."""
        # Create users and achievements
        users = []
        for i in range(1, 4):
            user = User(username=f"same_count_user_{i}", language="ru")
            test_db.add(user)
            users.append(user)
        
        achievements = []
        for i in range(1, 4):
            achievement = Achievement(
                name_ru=f"Достижение {i}",
                name_en=f"Achievement {i}",
                description_ru=f"Описание {i}",
                description_en=f"Description {i}",
                points=10
            )
            test_db.add(achievement)
            achievements.append(achievement)
        
        await test_db.commit()
        
        # Refresh objects
        for user in users:
            await test_db.refresh(user)
        for achievement in achievements:
            await test_db.refresh(achievement)
        
        # Give each user 2 achievements (same count)
        for user_idx in range(2):  # First 2 users
            for achievement_idx in range(2):  # First 2 achievements
                user_achievement = UserAchievement(
                    user_id=users[user_idx].id,
                    achievement_id=achievements[achievement_idx].id
                )
                test_db.add(user_achievement)
        
        await test_db.commit()
        
        # Test top by achievements - should return one of the users with 2 achievements
        response = await client.get("/stats/top-by-achievements")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] in [users[0].id, users[1].id]
        assert data["achievement_count"] == 2

    @pytest.mark.asyncio
    async def test_statistics_with_empty_database(self, client: AsyncClient, test_db: AsyncSession):
        """Test all statistics endpoints with empty database."""
        # Test all endpoints with no data
        endpoints = [
            "/stats/top-by-achievements",
            "/stats/top-by-points",
            "/stats/min-max-points-difference",
            "/stats/7-day-streak-users"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            
            if endpoint == "/stats/7-day-streak-users":
                assert data == []
            elif endpoint == "/stats/min-max-points-difference":
                assert "message" in data
            else:
                assert data["message"] == "No users with achievements found"