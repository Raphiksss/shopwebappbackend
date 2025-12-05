from .views import router as api_v1_router
from fastapi import APIRouter
from .services import rabbits_router

router = APIRouter()

router.include_router(api_v1_router, prefix = "/api/v1")
router.include_router(rabbits_router, prefix = "/api/v1")