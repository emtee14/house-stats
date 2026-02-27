from fastapi import APIRouter
from app.routes import auth, health

router = APIRouter()

router.include_router(health.router, prefix="/health")
router.include_router(auth.router, prefix="/auth")