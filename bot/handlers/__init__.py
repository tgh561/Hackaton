from .start import router as start_router
from .auth import router as auth_router
from .admin import router as admin_router

routers = [
    start_router,
    auth_router,
    admin_router,
]