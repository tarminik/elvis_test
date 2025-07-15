"""Statistics service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, text
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.models import User, Achievement, UserAchievement


class StatisticsService:
    """Statistics service for business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_top_by_achievements(self) -> Dict[str, Any]:
        """Get user with most achievements (count)."""
        result = await self.db.execute(
            select(
                User.id,
                User.username,
                func.count(UserAchievement.id).label("achievement_count")
            ).join(
                UserAchievement, User.id == UserAchievement.user_id
            ).group_by(
                User.id, User.username
            ).order_by(
                desc("achievement_count")
            ).limit(1)
        )
        
        top_user = result.first()
        if not top_user:
            return {"message": "No users with achievements found"}
        
        return {
            "user_id": top_user.id,
            "username": top_user.username,
            "achievement_count": top_user.achievement_count
        }
    
    async def get_top_by_points(self) -> Dict[str, Any]:
        """Get user with most points (sum)."""
        result = await self.db.execute(
            select(
                User.id,
                User.username,
                func.sum(Achievement.points).label("total_points")
            ).join(
                UserAchievement, User.id == UserAchievement.user_id
            ).join(
                Achievement, UserAchievement.achievement_id == Achievement.id
            ).group_by(
                User.id, User.username
            ).order_by(
                desc("total_points")
            ).limit(1)
        )
        
        top_user = result.first()
        if not top_user:
            return {"message": "No users with achievements found"}
        
        return {
            "user_id": top_user.id,
            "username": top_user.username,
            "total_points": int(top_user.total_points)
        }
    
    async def get_min_max_points_difference(self) -> Dict[str, Any]:
        """Get users with min and max points difference."""
        # Get all users with their total points
        result = await self.db.execute(
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(Achievement.points), 0).label("total_points")
            ).outerjoin(
                UserAchievement, User.id == UserAchievement.user_id
            ).outerjoin(
                Achievement, UserAchievement.achievement_id == Achievement.id
            ).group_by(
                User.id, User.username
            ).order_by(
                "total_points"
            )
        )
        
        users_with_points = result.all()
        if len(users_with_points) < 2:
            return {"message": "Not enough users to calculate difference"}
        
        min_user = users_with_points[0]
        max_user = users_with_points[-1]
        
        return {
            "min_points_user": {
                "user_id": min_user.id,
                "username": min_user.username,
                "total_points": int(min_user.total_points)
            },
            "max_points_user": {
                "user_id": max_user.id,
                "username": max_user.username,
                "total_points": int(max_user.total_points)
            },
            "points_difference": int(max_user.total_points) - int(min_user.total_points)
        }
    
    async def get_7_day_streak_users(self) -> List[Dict[str, Any]]:
        """Get users with 7-day achievement streaks."""
        # SQL query to find users with 7 consecutive days of achievements
        query = text("""
            WITH user_achievement_dates AS (
                SELECT 
                    ua.user_id,
                    u.username,
                    DATE(ua.awarded_at) as achievement_date
                FROM user_achievements ua
                JOIN users u ON ua.user_id = u.id
                GROUP BY ua.user_id, u.username, DATE(ua.awarded_at)
            ),
            consecutive_days AS (
                SELECT 
                    user_id,
                    username,
                    achievement_date,
                    achievement_date - INTERVAL '1 day' * ROW_NUMBER() OVER (
                        PARTITION BY user_id 
                        ORDER BY achievement_date
                    ) as group_date
                FROM user_achievement_dates
            ),
            streak_groups AS (
                SELECT 
                    user_id,
                    username,
                    group_date,
                    COUNT(*) as consecutive_days_count,
                    MIN(achievement_date) as streak_start,
                    MAX(achievement_date) as streak_end
                FROM consecutive_days
                GROUP BY user_id, username, group_date
                HAVING COUNT(*) >= 7
            )
            SELECT 
                user_id,
                username,
                consecutive_days_count,
                streak_start,
                streak_end
            FROM streak_groups
            ORDER BY consecutive_days_count DESC, user_id
        """)
        
        result = await self.db.execute(query)
        streak_users = result.all()
        
        if not streak_users:
            return []
        
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "consecutive_days": user.consecutive_days_count,
                "streak_start": user.streak_start.isoformat(),
                "streak_end": user.streak_end.isoformat()
            }
            for user in streak_users
        ]