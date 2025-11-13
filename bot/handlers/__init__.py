from .start import router as start_router
from .admin import router as admin_router
from .inspector import router as inspector_router
from .supervisor import router as supervisor_router

routers = [
    start_router,
    admin_router,
    inspector_router,
    supervisor_router,
]