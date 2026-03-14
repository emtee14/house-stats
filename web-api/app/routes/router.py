from fastapi import APIRouter
from app.routes import auth, billing, health, houses, stats

router = APIRouter()

router.include_router(health.router, prefix="/health")
router.include_router(auth.router, prefix="/auth")
router.include_router(billing.router, prefix="/billing")
router.include_router(stats.router, prefix="/stats")
router.include_router(houses.router, prefix="/houses")
