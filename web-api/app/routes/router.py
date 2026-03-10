from fastapi import APIRouter
from app.routes import auth, health, stats

router = APIRouter()

router.include_router(health.router, prefix="/health")
router.include_router(auth.router, prefix="/auth")
router.include_router(stats.router, prefix="/stats")
