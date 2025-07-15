"""User API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    service = UserService(db)
    return await service.create_user(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID."""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all users."""
    service = UserService(db)
    return await service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}/achievements")
async def get_user_achievements(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user achievements in user's language."""
    service = UserService(db)
    return await service.get_user_achievements(user_id)