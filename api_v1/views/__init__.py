from fastapi import APIRouter
from .users import router as users_router
from .products import router as prod_router
from .cart import router as cart_router
from .favorites import router as favorites_router
from .categories import router as categories_router
from .orders import router as orders_router
from .auth import router as auth_router
from .settings import router as project_settings_router

router = APIRouter()
router.include_router(prod_router, prefix = "/products")
router.include_router(cart_router, prefix = "/cart")
router.include_router(users_router, prefix = "/users")
router.include_router(favorites_router, prefix = "/favorites")
router.include_router(categories_router, prefix = "/categories")
router.include_router(orders_router, prefix = "/orders")
router.include_router(auth_router, prefix = "/auth")
router.include_router(project_settings_router,prefix="/settings")