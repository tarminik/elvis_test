"""Main FastAPI application."""

from fastapi import FastAPI
from app.api.users import router as users_router
from app.api.achievements import router as achievements_router
from app.api.statistics import router as statistics_router

app = FastAPI(
    title="Achievements API",
    description="API для управления достижениями пользователей",
    version="1.0.0"
)

# Include routers
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(achievements_router, prefix="/achievements", tags=["achievements"])
app.include_router(statistics_router, prefix="/stats", tags=["statistics"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Achievements API is running!"}